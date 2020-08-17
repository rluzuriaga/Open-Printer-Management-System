# Open Printer Management System (OPMS)

A Django project to easily view and manage multiple printer toner data.

![Version badge](https://img.shields.io/badge/Version-1.1.0-green)

## [View demo site](https://rodrigoluzuriaga.com/demo/opms/how-to)

![OPMS Gif demo 1.0.0](https://raw.githubusercontent.com/rluzuriaga/Open-Printer-Management-System/master/Open_Printer_Management_System/static/gif/OPMS-1.0.0.gif)

<br />

## How to install

### Prerequisites
* Ubuntu 18.04 (Desktop version is fine or you can use the Server version if you know what you are doing). Ubuntu 20.04 should be fine but has not been tested yet.
* Python 3.6 or newer (is included in Ubuntu but just putting it here just in case)
* sudo user account (can be done with the root user but for security reasons I don't recommend it)

### 1. Clone the repository
Clone the repository using the command: `git clone https://github.com/rluzuriaga/Open-Printer-Management-System.git` and then change directory into it using `cd Open-Printer-Management-System` <br />
I recommend cloning the repository your home directory, that means the path to the project would be `/home/username/Open-Printer-Management-System`

### 2. Run setup script
Once in the `Open-Printer-Management-System` directory, sun the command `./setup.sh` .  **Make sure you don't run it as sudo!**

The program will ask for the sudo password, the database you want to use, your time zone, and then how often the you want the system to update the toner data by itself. I tried to make the setup file self explanatory but if you face any issues, please don't hesitate to submit an issue.


### 3. Start using the system
If everything installed successfully, you should be able to go to a web browser and enter the IP address of the server and you should see this site.
<br />
![OPMS start image](https://raw.githubusercontent.com/rluzuriaga/Open-Printer-Management-System/master/Open_Printer_Management_System/static/images/site_example.png)
<br/>
From there you can start using the system.


<br />

## Docker support coming soon!



<br />

## How can I help?

If you are a developer with Python/Django or front-end experience and would like to help, go ahead and fork the repository and make a pull request. <br />
I am not a front-end developer, so I decided to use a simple Bootstrap template. If you would like to help by designing and implementing a better design for this project, please make a pull request or contact me using the contact form on [my website.](https://rodrigoluzuriaga.com/#contact)

If you find an issue or have any ideas for more things to implement, you can create an issue and I will take a look at it. Your issue/request may have already been posted so take a look at the issues already created first.

<br />

## License

The software is licensed under the MIT license. See the [LICENSE](https://github.com/rluzuriaga/Open-Printer-Management-System/blob/master/LICENSE) file for full copyright and license text. The short version is that you can do what you like with the code, as long as you say where you got it.
