# Cloning Your ADFS Portal for Security Awareness
In a previous commit, I showed you how you can [Clone Citrix Storefronts](https://github.com/gh0x0st/adfs_cloner) and incorporate custom PHP pages to capture credentials. Today, I'd like to show you the same concept, but this time we'll be targeting user portals for Active Directory Federation Services (ADFS), which is much easier.

## Disclaimer

This repository and the data provided has been created purely for the purposes of academic research and for the development of effective security techniques and is not intended to be used to attack systems except where explicitly authorized. It is your responsibility to obey all applicable local, state and federal laws. 

Project maintainers assume no liability and are not responsible for any misuse or damage caused by the data therein.

## Active Directory Federation Services
ADFS is a technology developed by Microsoft to provide users with single sign-on access to systems. This includes organizations that utilize Office 365 and Active Directory (AD) to provide seamless access to company resources. 

## Boots on the Ground
Before we jump into the attacker machine setup, I wanted to provide more sustenance on the process of cloning these type of pages because there's much to learn when you read the source.

1. Enumerating for ADFS
2. Root-Relative vs Absolute Links
3. Form Method Post Actions
4. Attacker Machine Setup

## Enumerating for ADFS
Before you work towards cloning an ADFS user portal, you need to find out if the company you're going to assess has one and if they do, how will you find it?

### Google Dorking
A potential quick win for you is to utilize Google Dorking, which is just a term to describe using advanced search queries within Google to identify indexed services. If you're lucky, the domain you're targeting may have it listed here, but even if it doesn't show here, it doesn't mean that it doesn't exist.

```
intitle:Sign In inurl:/adfs/ls/?wa=wsignin1.0 inurl:example.com
```

### End User Method
The more reliable method is to utilize Microsoft directly, by simply acting like you're an end user. After you visit https://www.office.com/login?es=Click&ru=%2F, you will be presented with a logon page and all you'll need to do is type a redundant username, but include the domain you intend to test for. If the domain has an ADFS user portal, you will get redirected to the user portal for that domain.

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/user-portal-redir.png?raw=true "user-portal-redirect")

Behind the scenes, if you run your connection through Burp, you'll be able to see the FederationRedirectUrl that contains the URL we want in the response. Keep in mind that if you browse to the complete URL, you'll see the full portal including the logon fields, but if you omit pieces of the URL, it'll likely error and show a broken page when you attempt to browse to it.

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/burp-portal-redir.png?raw=true "burp-portal-redirect")

### Root-Relative vs Absolute Links
Most web pages include resources that are found off the web root or other third party resources in order to build the page. If you were to save the index file of your ADFS user portal onto your local pc and try to view the page, it'll either be blank or otherwise broken because it's looking off your root for required resources. Let me show you what I mean:

I've included a sample of a hyperlink reference that you'll need to fix. When you see links, such as src="/ or href="/, those are root-relative links. In order for your clone to work, you need to replace these links with the absolute link to the required resource. Without this, your page will not render properly. 

For example, if your base url is 'https://fake.example.com' then `href="/adfs"`should become `href="https://fake.example.com/adfs"`. There are a few occurrences of this throughout the index file, which also includes the declarations for `background-image:url`. If you're ensure if your base URL is correct, then you can view the source of the original page and hover over the link to show the absolute path.

```HTML
<link rel="stylesheet" type="text/css" href="/adfs/portal/css/style.css?id=23456789DFGHJKL56710010AASSADASD5" /><style>.illustrationClass {background-image:url(/adfs/portal/illustration/illustration.jpg?id=23456789DF2212141GHJKL5671sadadasdasd0010AASSADASD);}</style>
```

Take the time to read and go through the source code of the index page to get an understanding of what it's going to do when it's launched. If you want to write your own script for this, make one change at a time and make sure it works before moving on.

### Form Method Post Actions
To keep this simple, we are going to use a custom php page and designate our form method action to point to the root-relative link of this page, since we're hosting this on our attacker machine. I included a very quick and simple php page in this repository. What this file will do is when a post is submitted, it will send the data to our php page, from which it'll append a log with the username, password, ip and user agent.

**IMPORTANT** 
  * Avoid keeping the log file in the web root *(change this in line 41)*
  * www-data needs to be able to write to the log file

## Attacker Machine Setup
Now that we have a better understanding of what we're trying to accomplish, let's fire up our Kali machine and get to work.

1. Enumerate the ADFS URL and Clone the Webpage
2. Create Our post.php File	
3. Identify the Username/Password Field Names
4. Create Log File for post.php and Assign Proper Permissions
5. Start Apache and Test

### Enumerate the ADFS URL and Clone the Webpage
I wrote a simple python script called 'adfs-cl.py' to facilitate the enumeration, cloning and cleaning process, that works as of the date of posting this. It currently has three parameters, the target domain, the path to the action php file and a switch to clone or not.

Once you run the script, it will:

* Check if the domain has an ADFS user portal by making a post request with an arbitrary username
* Print the full URL if found
* Check if you designated the script to clone, if so, it'll write the content to index.html off the current directory
   * Adjust the link references
   * Run additional clean up steps

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/adfs-cl.png?raw=true "adfs-cl")

### Create Our post.php File	
You can utilize your own php file, or copy down the one I provided in the repository. Depending on the route you want to take, you can keep this as a credential harvester or replace that functionality with an awareness landing page for your organization. 

If you go the credential harvester route, be sure to modify the last line of the file which is a page refresh to a designated URL. To help stay under the radar, set this to the actual URL. The reason for this is the user might not get suspicious and simply try again, getting the intended content and moving along.

```HTML
<meta http-equiv="refresh" content="0; url=https://real.example.com" />
```

### Identify the Username/Password Field Names
Within our post.php file we are capturing the username and password from the POST so we can append it to a log entry. A common mistake people make is assume the input name is going to be username/password respectively, or they print out the entire POST array, which is ugly. This is where reading the source code will help us out. 

For example, using the below snippet we can see the input field for the username and password. We got lucky here, but not every web application is like this.

```HTML
<input id="userNameInput" name="UserName" type="email" value="" tabindex="1" class="text fullWidth" spellcheck="false" placeholder="someone@example.com" autocomplete="off"/>
<input id="passwordInput" name="Password" type="password" tabindex="2" class="text fullWidth" placeholder="Password" autocomplete="off"/>
```

Using the information we verified, we can test to ensure we are capturing the credentials.

```PHP
<?php
$username = $_POST["UserName"];
$password = $_POST["Password"];
echo "Username: $username | Password: $password";
?>
```

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/post-credentials.png?raw=true "post-credentials")

### Create Log File for post.php and Assign Proper Permissions
As I mentioned previously, you should not create your log file in the web root, unless you want someone to snoop in on your results if they manage to find the file. Just make sure you give www-data permissions to write to the file itself. 

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/capture-txt.png?raw=true "capture-txt")

### Start Apache and Test
Now that we have everything loaded up, browse to http://127.0.0.1, enter in some credentials and see if you can successfully log the entries to a log file. If everything works from here, then your next step is simple; engineer a solution to get your staff to connect to the site. Get creative.

![Alt text](https://github.com/gh0x0st/adfs_cloner/blob/master/Screenshots/captured-creds.png?raw=true "captured-creds")

## Putting it all together

Regardless of the platform you're cloning, this is a very fun process. When you take the time to craft your own solution, you'll benefit so much more. It's very common to lose focus on the awareness aspect and our efforts may turn into ego boosters; avoid doing that. Just keep the following points in the back of your mind before you start to execute your exercise:

1. Don't social engineer your employees just to single them out and shame them
2. Utilize the engagement to identify gaps in your awareness program
3. When staff fail, walk them through some of the red flags that could've helped them, such as a wrong url or no SSL icon
4. Reward the people who report your campaign - these are your security heroes

Be informed, be secure.
