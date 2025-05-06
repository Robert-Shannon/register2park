# Automated Parking Registration

This repository contains a Python script that automates the process of registering for guest parking at a residential complex through the Register2Park website. The script is scheduled to run daily at 12 PM CST using GitHub Actions.

## How It Works

1. The script uses Selenium WebDriver to control a headless Chrome browser
2. It navigates to register2park.com and enters the required registration information
3. The registration is set up for a 24-hour period (today to tomorrow)
4. Optionally sends an email confirmation to the provided email address

## Setup Instructions

### 1. Fork this repository

Start by forking this repository to your own GitHub account.

### 2. Set up repository secrets

You need to add the following secrets to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each of these secrets:

| Secret Name        | Description                           |
|--------------------|---------------------------------------|
| PROPERTY_NAME      | Your apartment complex's name         |
| UNIT_NUMBER        | Your apartment unit number            |
| RESIDENT_NAME      | Resident name                         |
| GUEST_NAME         | Guest's name                          |
| GUEST_PHONE        | Guest's phone number                  |
| VEHICLE_MAKE       | Vehicle manufacturer (e.g., Toyota)   |
| VEHICLE_MODEL      | Vehicle model (e.g., Camry)           |
| VEHICLE_PLATE      | License plate number                  |
| NOTIFICATION_EMAIL | Email for confirmation (optional)     |

### 3. Enable GitHub Actions

1. Go to the "Actions" tab in your repository
2. Enable workflows if they're not already enabled

The parking registration will now run automatically every day at 12 PM CST.

## Manual Trigger

You can also trigger the registration manually:

1. Go to the "Actions" tab in your repository
2. Select the "Daily Parking Registration" workflow
3. Click "Run workflow"

## Troubleshooting

If the registration fails, check the GitHub Actions logs:

1. Go to the "Actions" tab
2. Click on the most recent workflow run
3. Review the logs for error messages

Common issues:
- Missing or incorrect environment variables
- Form layout changes on the website
- Network connectivity issues

## Manual Local Testing

To test the script locally in your terminal:

```bash
# Create a .env file with your credentials
# See example .env.example file

# Install dependencies
pip install selenium python-dotenv

# Run in visible browser mode for testing
python register_parking.py --debug

# Run in headless mode with email notification
python register_parking.py --notify

# Run with verbose logging for troubleshooting
python register_parking.py --verbose
```

## Script Features

- **Headless Operation**: Runs without a visible browser when deployed
- **Debug Mode**: Shows browser actions with `--debug` flag
- **Email Notifications**: Sends confirmation email to the specified address
- **Error Handling**: Robust error handling for more reliable operation
- **Verbose Logging**: Detailed logging to help diagnose issues

## Customization

You can modify the script to adjust:
- Registration times (in the GitHub Actions workflow file)
- Vehicle information (through environment variables)
- Browser behavior (in the `setup_driver` function)

## Security Note

This repository uses GitHub Secrets to store your personal information securely. However, be cautious when sharing access to this repository or making it public.