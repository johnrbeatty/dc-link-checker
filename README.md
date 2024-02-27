# DC Link Checker
DC Link Checker is a link checking tool for Digital Commons repository administrators. The Digital Commons platform allows 
an administrator to add links to external documents. This is usually used to highlight documents that cannot be posted 
on the repository. It also allows administrators to include links to sites where users can purchase a book highlighted 
in a book gallery.

The platform, however, offers no easy way to check these external links to make sure that they are still active. DC 
Link Checker offers a simple way to check all the links of either type to make sure they are still active. It's a simple 
command-line tool that operates on a Content Inventory spreadsheet. It takes the spreadsheet as input and pulls out 
either the externally linked documents or the buy links from the book galleries and then attempts to fetch the page at 
the link. All of the responses are saved to a spreadsheet that also includes some other key information to help the 
administrator find the links on the repository so they can be updated. 

## Installation
To use DC Link Checker, clone the repository and download and install Python 3 and the following libraries:

* Pandas (2.2.0)
* Requests (2.31.0)
* Openpyxl (3.2.0b1)

The listed version of each library was used for development. Some older and presumably newer 
versions will work, but this has not been tested. 

## Usage

After installation, DC Link Checker can be called from the command line using the Python executable:

> (path)/py.exe (path)/checklinks.py (input file) (options)

Alternately, you can add the link to the Python interpreter and make the script executable. 

### Options
-h or --help: Show the options

-o <output file> or --output-file <output file>: Specify the filename to use for the saved spreadsheet with the 
response codes. If not set, the program will use the input filename with "-checked" added before the file extension. 

-v or --verbose: Show status messages. If the verbose option is on, the number of links found will be printed, and 
then each URL tried will be printed, followed by the http response code. This can be useful as a progress report and 
in case something goes wrong before the output spreadsheet is saved. I have not yet completed all of the error 
trapping and only a generic error is saved to the spreadsheet. Setting the verbose option will allow you to see the 
actual error. 

-b or --buy-links: Gather and check the buy links in the book galleries. The default gathers all of the externally 
linked documents attached to all records. These are the ones set in the individual records instead of uploading a 
document. 

-t <seconds> or --timeout <seconds>: Set the timeout for the http requests to the specified number of seconds. The 
default is 10 seconds. I have found this to be generally long enough to obtain a response from most sites, but if you 
are having a problem with timeouts, you can set it longer. 

### Problem websites

Some websites will treat DC Link Checker as a web scraper and refuse the connection with a 403 error. In order to 
minimize rejections, I have set up headers to make it look more like a regular web browser. Each set of links is 
browsed over a single session, which allows the websites to set cookies. In testing, I have been able to successfully 
connect to almost all of the websites that initially refused a connection. There are still some big publishers that 
are filtering the program and returning a 403. Most of these sites are using Cloudflare bot detectors. Getting around 
this will require using a headless browser or one of the web scraper libraries that attempt to work around these 
protections. Many of these require API calls and would, therefore, require users to set up an account to use. For the 
moment, these results are few enough that I'm not worrying about it. 

### 429 Errors/Too Many Requests

In the initial tests, some sites refused a connection because there were so many attempts coming in quickly. I have 
added two random timers to help prevent this. One adds a 10 to 30-second delay between any back-to-back attempts to 
connect to the same website. The other adds a 30 to 60-second delay before retrying a connection that was refused with 
a 429 error. 

### Output options

Right now, only a spreadsheet export is available. I may add a CSV option. The file is not exported line by line, but 
dumped into a file at the end. That should probably be changed. 

### Other issues

I have not implemented any real error trapping. The error I have encountered most is http timeout. Right now, only the 
word "Error" is added to the output spreadsheet, and the actual error is returned only if verbose mode is used. 

Currently, there is no way to start processing a list partway through. I would like to implement this once I have 
changed the code to write the output spreadsheet line by line. I would also like to add an append option to the output 
spreadsheet (or CSV file).