##Web Portal Automation

This script leverages Selenium WebDriver to automate interactions with a web portal, specifically designed for managing legal appeals in "Portal Informacyjny Sądów Powszechnych".

The script sets up a Chrome WebDriver with customizable options, including the ability to run headless in the background. 
'''python
options = Options()
options.add_argument("--headless")
'''
A login function navigates to the portal's login page and authenticates using provided credentials. The script then handles potential pop-ups and navigates to a specific subaccount management page. The core functionality revolves around processing appeals across multiple jurisdictions. It iterates through different appeal options, applies filters to display more items per page, and sorts the results based on granted access.

A key feature is the 'clicker' function, which automatically grants access to pending requests if available. This process is repeated for each jurisdiction, streamlining what could otherwise be a time-consuming manual task for the client.
