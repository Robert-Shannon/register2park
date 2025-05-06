import os
import time
import logging
import argparse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# Try to import dotenv for local development
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads the variables from .env
    print("Loaded environment from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# Set up logging - console only, no file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
PROPERTY_NAME = os.environ.get('PROPERTY_NAME', 'Sondery, The')
UNIT_NUMBER = os.environ.get('UNIT_NUMBER')
RESIDENT_NAME = os.environ.get('RESIDENT_NAME')
GUEST_NAME = os.environ.get('GUEST_NAME')
GUEST_PHONE = os.environ.get('GUEST_PHONE')
VEHICLE_MAKE = os.environ.get('VEHICLE_MAKE')
VEHICLE_MODEL = os.environ.get('VEHICLE_MODEL')
VEHICLE_PLATE = os.environ.get('VEHICLE_PLATE')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')

def setup_driver(headless=True):
    """Set up and return a configured Chrome webdriver."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # Using newer headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def safe_click(driver, selector_type, selector, timeout=5, description="element"):
    """Try to click an element with retries."""
    for attempt in range(3):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((selector_type, selector))
            )
            driver.execute_script("arguments[0].click();", element)
            logger.info(f"Clicked on {description}")
            return True
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/3: Failed to click on {description}: {str(e)}")
            time.sleep(1)
    
    logger.error(f"Failed to click on {description} after multiple attempts")
    return False

def safe_send_keys(driver, selector_type, selector, text, timeout=5, description="field"):
    """Try to send keys to an element with retries."""
    for attempt in range(3):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((selector_type, selector))
            )
            element.clear()
            element.send_keys(text)
            logger.info(f"Entered text in {description}: {text}")
            return True
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/3: Failed to enter text in {description}: {str(e)}")
            time.sleep(1)
    
    logger.error(f"Failed to enter text in {description} after multiple attempts")
    return False

def check_element_exists(driver, selector_type, selector, timeout=5, description="element"):
    """Check if an element exists on the page."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((selector_type, selector))
        )
        logger.info(f"Found {description}")
        return True
    except Exception as e:
        logger.info(f"Element {description} not found: {str(e)}")
        return False

def register_parking(headless=True, debug_mode=False):
    """Main function to handle the parking registration process."""
    logger.info("Starting parking registration process")
    
    # Check if required environment variables are set
    required_vars = [
        'UNIT_NUMBER', 'RESIDENT_NAME', 'GUEST_NAME', 
        'GUEST_PHONE', 'VEHICLE_MAKE', 'VEHICLE_MODEL', 'VEHICLE_PLATE'
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    driver = None
    try:
        driver = setup_driver(headless=headless)
        
        # Step 1: Navigate directly to the registration page
        driver.get("https://www.register2park.com/register")
        logger.info("Navigated to Register2Park registration page")
        
        # Step 2: Enter property name
        property_entered = safe_send_keys(
            driver, By.ID, "propertyName", PROPERTY_NAME, 
            description="property name field"
        )
        if not property_entered:
            return False
        
        # Step 3: Click Next button
        next_clicked = safe_click(
            driver, By.ID, "confirmProperty", 
            description="Next button"
        )
        if not next_clicked:
            return False
        
        time.sleep(2)  # Wait for property list to load
        
        # Step 4: Select the property - FIXED VERSION
        # First try to find the select button directly
        try:
            select_buttons = driver.find_elements(By.CLASS_NAME, "select-property")
            logger.info(f"Found {len(select_buttons)} select buttons")
            
            if len(select_buttons) > 0:
                # Click the first select button (should be our property)
                select_buttons[0].click()
                logger.info("Clicked on the first select button")
            else:
                # If no buttons found, try different approaches
                logger.warning("No select buttons found with class 'select-property'")
                
                # Approach 1: Try clicking any button with 'Select' text
                select_text_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Select')]")
                if len(select_text_buttons) > 0:
                    select_text_buttons[0].click()
                    logger.info("Clicked on button with 'Select' text")
                else:
                    # Approach 2: Try using JavaScript to find and click the button
                    logger.warning("No buttons found with 'Select' text, trying JavaScript approach")
                    driver.execute_script("""
                        // Look for any button that contains 'Select'
                        const buttons = document.querySelectorAll('button');
                        for (const button of buttons) {
                            if (button.textContent.includes('Select')) {
                                button.click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    logger.info("Attempted to click Select button via JavaScript")
        except Exception as e:
            logger.error(f"Failed to select property: {str(e)}")
            return False
        
        # Step 5: Handle the rules popup - wait for it and click Continue
        time.sleep(2)  # Give popup time to appear
        
        popup_continue_clicked = safe_click(
            driver, By.XPATH, "//button[contains(text(), 'Continue')]", 
            description="Continue button on rules popup"
        )
        if not popup_continue_clicked:
            # Try alternative approach with JavaScript
            try:
                driver.execute_script("""
                    const buttons = document.querySelectorAll('button');
                    for (const button of buttons) {
                        if (button.textContent.includes('Continue')) {
                            button.click();
                            return true;
                        }
                    }
                    return false;
                """)
                logger.info("Attempted to click Continue button via JavaScript")
            except Exception as e:
                logger.error(f"Failed to click Continue button with JavaScript: {str(e)}")
                return False
        
        # Step 6: Click on Visitor Parking
        time.sleep(2)  # Give page time to load
        
        visitor_parking_clicked = safe_click(
            driver, By.XPATH, "//button[contains(text(), 'Visitor Parking')]", 
            description="Visitor Parking button"
        )
        if not visitor_parking_clicked:
            # Try alternative approach with JavaScript
            try:
                driver.execute_script("""
                    const buttons = document.querySelectorAll('button');
                    for (const button of buttons) {
                        if (button.textContent.includes('Visitor Parking')) {
                            button.click();
                            return true;
                        }
                    }
                    return false;
                """)
                logger.info("Attempted to click Visitor Parking button via JavaScript")
            except Exception as e:
                logger.error(f"Failed to click Visitor Parking button with JavaScript: {str(e)}")
                return False
        
        # Step 7: Fill out the registration form
        time.sleep(2)  # Give form time to load
        
        # Fill in the form using the correct IDs from the HTML
        
        # Apartment Number
        apt_filled = safe_send_keys(
            driver, By.ID, "vehicleApt", 
            UNIT_NUMBER, description="Apartment Number field"
        )
        if not apt_filled:
            return False
        
        # Resident Name
        resident_filled = safe_send_keys(
            driver, By.ID, "vehicleResidentName", 
            RESIDENT_NAME, description="Resident Name field"
        )
        if not resident_filled:
            return False
        
        # Guest Name
        guest_filled = safe_send_keys(
            driver, By.ID, "vehicleGuestName", 
            GUEST_NAME, description="Guest Name field"
        )
        if not guest_filled:
            return False
        
        # Guest Phone
        phone_filled = safe_send_keys(
            driver, By.ID, "vehicleGuestPhone", 
            GUEST_PHONE, description="Guest Phone field"
        )
        if not phone_filled:
            return False
        
        # Make
        make_filled = safe_send_keys(
            driver, By.ID, "vehicleMake", 
            VEHICLE_MAKE, description="Make field"
        )
        if not make_filled:
            return False
        
        # Model
        model_filled = safe_send_keys(
            driver, By.ID, "vehicleModel", 
            VEHICLE_MODEL, description="Model field"
        )
        if not model_filled:
            return False
        
        # License Plate
        plate_filled = safe_send_keys(
            driver, By.ID, "vehicleLicensePlate", 
            VEHICLE_PLATE, description="License Plate field"
        )
        if not plate_filled:
            return False
        
        # Confirm License Plate
        confirm_plate_filled = safe_send_keys(
            driver, By.ID, "vehicleLicensePlateConfirm", 
            VEHICLE_PLATE, description="Confirm License Plate field"
        )
        if not confirm_plate_filled:
            return False
        
        # Step 8: Click Next to submit the form
        submit_clicked = safe_click(
            driver, By.ID, "vehicleInformation", 
            description="Next button to submit form"
        )
        if not submit_clicked:
            # Try JavaScript approach
            try:
                driver.execute_script("document.getElementById('vehicleInformation').click();")
                logger.info("Clicked Next button via JavaScript")
            except Exception as e:
                logger.error(f"Failed to click Next button with JavaScript: {str(e)}")
                return False
        
        # Step 9: Wait for confirmation page to load
        logger.info("Waiting for confirmation page to load...")
        time.sleep(8)  # Increased wait time for confirmation page
        
        # Check for confirmation message elements
        approved_msg = check_element_exists(
            driver, By.XPATH, "//h2[contains(text(), 'Approved')]",
            description="Approved message"
        )
        
        circle_success = check_element_exists(
            driver, By.CLASS_NAME, "circle-success",
            description="Success circle"
        )
        
        # Extract confirmation code if available
        try:
            confirmation_code_element = driver.find_element(By.XPATH, "//h3[contains(text(), '')]")
            confirmation_code = confirmation_code_element.text.strip()
            logger.info(f"Registration successful! Confirmation code: {confirmation_code}")
        except Exception:
            # Try another approach
            try:
                confirmation_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Confirmation Code')]")
                logger.info("Found confirmation code reference")
                confirmation_code = "Found but couldn't extract"
            except Exception:
                logger.info("Couldn't find confirmation code")
                confirmation_code = None
        
        if approved_msg or circle_success:
            logger.info("Registration successful!")
            
            # Handle email confirmation if requested
            if NOTIFICATION_EMAIL:
                # Debug: log page source to understand what we're looking at
                if debug_mode:
                    logger.info("Current page source before email button interaction:")
                    logger.info("=== PAGE SOURCE START ===")
                    logger.info(driver.page_source[:500] + "...")  # Just the start
                    logger.info("=== PAGE SOURCE END ===")
                
                # Wait longer for the button to be enabled
                logger.info("Waiting for email button to be enabled...")
                time.sleep(5)  # Give extra time for any page scripts to run
                
                # First check if the email button is disabled
                try:
                    email_button = driver.find_element(By.ID, "email-confirmation")
                    
                    # Get button text and disabled state
                    button_text = email_button.text
                    is_disabled = email_button.get_attribute("disabled") is not None
                    
                    logger.info(f"Email button found: Text='{button_text}', Disabled={is_disabled}")
                    
                    if is_disabled:
                        logger.info("Button is disabled, waiting for it to become enabled...")
                        # Wait for the button to become enabled (up to 15 seconds)
                        wait_time = 15
                        for i in range(wait_time):
                            is_still_disabled = email_button.get_attribute("disabled") is not None
                            if not is_still_disabled:
                                logger.info(f"Button became enabled after {i+1} seconds")
                                break
                            logger.info(f"Still disabled, waiting... ({i+1}/{wait_time})")
                            time.sleep(1)
                        
                        # Refresh the element reference
                        email_button = driver.find_element(By.ID, "email-confirmation")
                    
                    # Check if it's now enabled
                    if email_button.get_attribute("disabled") is None:
                        logger.info("Email button is now enabled, clicking it")
                        email_button.click()
                        logger.info("Clicked email confirmation button")
                    else:
                        logger.warning("Email button still disabled, trying JavaScript bypass")
                        driver.execute_script("""
                            document.getElementById('email-confirmation').removeAttribute('disabled');
                            document.getElementById('email-confirmation').click();
                        """)
                        logger.info("Used JavaScript to enable and click email button")
                except Exception as e:
                    logger.warning(f"Could not interact with email button normally: {e}")
                    # Try alternative approach using JavaScript
                    try:
                        driver.execute_script("""
                            var emailBtn = document.getElementById('email-confirmation');
                            if(emailBtn) {
                                emailBtn.disabled = false;
                                emailBtn.click();
                                console.log('Email button clicked via JavaScript');
                            } else {
                                console.log('Email button not found');
                            }
                        """)
                        logger.info("Used JavaScript to find and click email button")
                    except Exception as e2:
                        logger.error(f"JavaScript approach also failed: {e2}")
                
                # Wait for modal to appear
                logger.info("Waiting for email modal to appear...")
                time.sleep(4)
                
                # Debug - log what modals might be present
                if debug_mode:
                    modals = driver.find_elements(By.CLASS_NAME, "modal")
                    logger.info(f"Found {len(modals)} modal elements")
                    for i, modal in enumerate(modals):
                        try:
                            modal_id = modal.get_attribute("id")
                            is_visible = modal.is_displayed()
                            modal_class = modal.get_attribute("class")
                            logger.info(f"Modal {i+1}: ID={modal_id}, Visible={is_visible}, Class={modal_class}")
                        except:
                            logger.info(f"Modal {i+1}: [Error getting attributes]")
                
                # Look for the email input field in the modal
                email_field_found = check_element_exists(
                    driver, By.ID, "emailConfirmationEmailView", 
                    timeout=5, description="Email field in popup"
                )
                
                if email_field_found:
                    # Enter email address
                    email_entered = safe_send_keys(
                        driver, By.ID, "emailConfirmationEmailView", 
                        NOTIFICATION_EMAIL, description="Email field"
                    )
                    
                    if email_entered:
                        logger.info(f"Email entered: {NOTIFICATION_EMAIL}")
                        
                        # Click Send button
                        logger.info("Attempting to click Send button")
                        send_clicked = safe_click(
                            driver, By.ID, "email-confirmation-send-view", 
                            timeout=5, description="Send email button"
                        )
                        
                        if send_clicked:
                            logger.info(f"Confirmation email send button clicked")
                            # Wait for confirmation alert
                            time.sleep(2)
                            
                            # Check for confirmation alert
                            try:
                                alert = driver.switch_to.alert
                                alert_text = alert.text
                                logger.info(f"Alert found: {alert_text}")
                                alert.accept()
                                logger.info("Alert accepted")
                            except:
                                logger.info("No JavaScript alert found - this is normal if confirmation was shown in page")
                                
                            logger.info("Email confirmation process completed")
                        else:
                            logger.warning("Failed to click send button")
                            # Try with JavaScript
                            try:
                                driver.execute_script("""
                                    document.getElementById('email-confirmation-send-view').click();
                                """)
                                logger.info("Clicked send button via JavaScript")
                                time.sleep(2)  # Wait for the operation to complete
                                logger.info("Email confirmation process completed via JavaScript")
                            except Exception as e:
                                logger.error(f"JavaScript click for send button failed: {e}")
                    else:
                        logger.warning("Failed to enter email address")
                else:
                    logger.warning("Email popup did not appear or couldn't find the email field")
                    
                    # Try to get all input fields as a diagnostic
                    try:
                        inputs = driver.find_elements(By.TAG_NAME, "input")
                        logger.info(f"Found {len(inputs)} input elements on page")
                        for i, input_el in enumerate(inputs[:5]):  # Show just first 5 to avoid log spam
                            input_id = input_el.get_attribute("id")
                            input_type = input_el.get_attribute("type")
                            logger.info(f"Input {i+1}: ID={input_id}, Type={input_type}")
                    except:
                        logger.info("Could not enumerate input fields")
            
            # Pause at the end if in debug mode
            if debug_mode:
                logger.info("DEBUG MODE: Pausing for 10 seconds at end for manual inspection")
                time.sleep(10)
            
            return True
        else:
            logger.error("Couldn't confirm registration success")
            
            # In debug mode, pause to inspect
            if debug_mode:
                logger.info("DEBUG MODE: Registration could not be confirmed. Pausing for manual inspection.")
                time.sleep(20)  # Longer pause for error inspection
                
            return False
            
    except Exception as e:
        logger.error(f"Error during registration process: {str(e)}")
        
        # In debug mode, pause to inspect
        if debug_mode and driver:
            logger.info("DEBUG MODE: Error occurred. Pausing for manual inspection.")
            time.sleep(20)  # Longer pause for error inspection
            
        return False
    finally:
        if driver:
            # Close the browser
            driver.quit()
            logger.info("Browser closed")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Register parking on Register2Park')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (visible browser)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging and pauses')
    args = parser.parse_args()
    
    # Check if running in debug mode
    debug_mode = args.debug or os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    verbose_mode = args.verbose or os.environ.get('VERBOSE_MODE', 'false').lower() == 'true'
    
    # Run the registration process
    success = register_parking(headless=not debug_mode, debug_mode=verbose_mode)
    
    # Exit with appropriate code
    exit(0 if success else 1)