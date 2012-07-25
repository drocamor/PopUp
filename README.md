PopUp 
=====
PopUp creates an ephemeral EC2 instance so you always have a good computer somewhere.

I have a crap laptop. It is slow and I tend to mess it up by installing lots of dumb software on it. I realized that frequently I want to have a good computer to screw around with. This computer may need to have a lot of RAM, CPU, fast Internet or a GPU or whatever. I also may just want another machine to install something weird on without worrying about destroying my own machine. 

I'm a huge AWS nerd, so what I had been doing was creating EC2 instances whenever I wanted to do something like this. There were a few issues with my approach:

* Starting and configuring an instance takes time and is a drag
* Once I've customized a computer I become attached to it, so I wouldn't terminate it. I'd end up with a computer just as messed up as my laptop. 
* I'll forget to stop/terminate it and end up paying a *huge* AWS bill. 

To help with this, I created PopUp. It is a simple python script that creates an instance, configures it, and sets up a timer that makes the instance terminate itself after a period of time. PopUp helps out by creating an SSH alias to make it easy to connect.

Usage
=====

This is pretty basic now, but to get started you need:

* An AWS account
* Your AWS creds in ~/.boto
* A security group
* An EC2 keypair
* A config file in ~/.popup.conf
* Python and boto

With this in place you can run popup.py start to create an instance. Enjoy!

Todos
=====
* PopUp makes sure you don't have an instance running already
* You can extend the time that an instance will run for
* There's a script to install and configure oh-my-zsh
* There's a script to install and configure DropBox

