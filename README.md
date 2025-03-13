# Google-Maps-SEO
This Node.js script utilizes Puppeteer and Express to create a visitable API to get the information of different businesses on Google Maps.

## Prerequisite
- Node.js and npm installed

## Installation
1. Clone the repository
2. Navigate to the project directory
3. Run `npm install` to install the dependencies

## Usage
1. Run `npm start` to start the server
2. Access the API at `http://localhost:10000/get_places`

## Key Features
- Data Scraping: The script scrapes data from Google Maps listings, extracting valuable information about businesses, such as their name, address, website, and contact details.
- Review Analysis: It extracts review counts and average ratings, providing insights into businesses' online reputation.
- Business Type Detection: The script identifies whether a business offers in-store shopping, in-store pickup, or delivery services.
- Operating Hours: It extracts information about the business's operating hours.
- Introduction Extraction: The script also scrapes introductory information about the businesses when available.
- Data Cleansing: It cleanses and organizes the scraped data, removing redundant or unnecessary columns.

## Based on an existing project:
https://www.linkedin.com/posts/zohaibbashir_python-data-webscraping-activity-7093920891411062784-flEQ