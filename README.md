# Automated Parking Registration

This repository contains a Python script that automates the process of registering for guest parking at a residential complex through the Register2Park website. The script is scheduled to run daily at 12 PM CST using GitHub Actions.

## How It Works

1. The script uses Selenium WebDriver to control a headless Chrome browser
2. It navigates to register2park.com and enters the required registration information
3. The registration is set up for a 24-hour period (today to tomorrow)
4. A screenshot is saved as a GitHub Actions artifact for verification

## Setup Instructions

### 1. Fork this repository

Start by forking this repository to your own GitHub account.

### 2. Set up repository secrets

You need to add the following secrets to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each of these secrets:

| Secret Name     | Description                               |
|-----------------|-------------------------------------------|
| PROPERTY_CODE   | Your apartment complex's property code    |
| FIRST_NAME      | Guest's first name                        |
| LAST_NAME       | Guest's last name                         |
| UNIT_NUMBER     | Your apartment unit number                |
| PHONE           | Contact phone number                      |
| EMAIL           | Contact email address                     |
| VEHICLE_MAKE    | Vehicle manufacturer (e.g., Ford)         |
| VEHICLE_MODEL   | Vehicle model (e.g., F150)                |
| VEHICLE_COLOR   | Vehicle color                             |
| VEHICLE_PLATE   | License plate number                      |
| VEHICLE_STATE   | State of license plate (default: TX)      |

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

If the registration fails, check the GitHub Actions logs and the screenshot artifact:

1. Go to the "Actions" tab
2. Click on the most recent workflow run
3. Scroll down to the "Artifacts" section
4. Download and check the "registration-screenshot" artifact

Common issues:
- Incorrect property code
- Form layout changes on the website
- Network connectivity issues

## Manual Local Testing

To test the script manually in the terminal:

```bash
# Run in visible browser mode for testing
python register_parking.py --debug --notify

# Run with email notification
python register_parking.py --notify
```



## Customization

You can modify the script to adjust:
- Registration times
- Vehicle information
- Number of days to register

## Security Note

This repository uses GitHub Secrets to store your personal information securely. However, be cautious when sharing access to this repository or making it public.