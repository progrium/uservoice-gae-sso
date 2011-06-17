# Uservoice SSO for Google Apps

This is an App Engine app intended to run on your Google Apps domain that gives you SSO for Uservoice using the user accounts in your domain.

## Setup

 * Create an App Engine app for your domain: http://appengine.google.com/a/<yourdomain>
 * Pick an unused name for your app and **make sure to use your domain for auth**
 * Download the source code here and edit the app.yaml to use the application name you chose.
 * Use the App Engine SDK to deploy
 * Browse to http://<appname>.appspot.com and put in your Uservoice account name, API key, and domain. Hit save.
 * Go to your Uservoice settings and under authentication options, select SSO and put in the URLs

## License

MIT