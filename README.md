<h1>COMP 4300 Project</h1>

<h2> QUIC vs TCP in a File Sharing Context </h2>
Welcome to the source code repository for my networking project!

In this repo, you will find all of the code that was used in my experiment.

If you want to run the application, download the files by clicking the green "Code" button near the "About" section. Next, click the "Download ZIP" button in the popup menu.

Lastly, follow the instructions in the URL:

https://youtu.be/e7I-2GpRhJ4

Watch a demo of the application here:

https://youtu.be/Onv691w0woQ

<h2>Commands</h2>

Once you have the code downloaded and setup, use the following commands.

<h4>Running the client:</h4>

python client.py [ip] [port] [tcp/quic] [username] [prod/debug]

<h4>Running the server:</h4>

python server.py [ip] [port] [tcp/quic] [prod/debug]

<h4>Running the unit_tests:</h4>

python -m unittest discover -v
