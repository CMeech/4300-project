ACCESS_DENIED="\nAccess Denied."
ACCESS_GRANTED="\nAccess granted to user {}."
ACCESS_REVOKED="\nAccess revoked for user {}."
BENCHMARK="Benchmark -> Chunk Size: {}, Number of Chunks: {}, Time: {}."
CHUNK_RECEIVED="Received the chunk: {}"
CHUNK_SENT="Sent the chunk: {}"
CLIENT_NAME="{}"
CLIENTS="\nThe following clients exist:"
CONNECTING="Connecting to server at {}:{}"
DATA_ERROR="\nThere was an issue while getting data from the server."
DELETE_ERROR="\nError trying to delete the specified file. Ensure the given values are correct."
DOWNLOAD_ERROR="Download failed for file {} and user {}."
DOWNLOADING="Downloading the file..."
EMPTY=""
EXPERIMENT_ERROR="Failed to open a file to store the test. See the debug logs for the error."
EXPERIMENT_SAVE_ERROR="An error occurred while saving the experiment data. See the debug logs."
EXPERIMENT_SAVED="Successfully saved the experiment data in a csv."
FILE="Filename: {}, Owner: {}\n"
FILE_CREATED="\nFile {} created successfully."
FILE_DOWNLOADED="\nFile {} downloaded successfully."
FILE_DELETED="Deleted the file successfully."
FILE_SENT="File was sent successfully."
FILE_UPLOADED="\nFile uploaded successfully."
FILES="\nYou have access to the following files:"
GENERIC_ERROR="\nSomething went wrong. Make sure the values you provided are correct."
GRANT_ERROR="\nUnable to grant access to that user. Ensure all provided values are correct."
HELP="""\nAvailable commands:

Automates num_tests downloads for the given file. Stores the result in
a file labeled by experiment_name. Chunk size can be 'small' or 'large'.
--------
automate [experiment_name] [num_tests] [filename] [owner] [chunk_size]

Deletes the given file from the server.
--------
delete [filename]

Downloads the file specified that is owned by the given owner.
Chunk size can be 'small' or 'large'.
--------
download [filename] [owner] [chunk_size]

Lists the files you have access to along with their owners.
--------
files

Gives the user access to a file you uploaded.
--------
grant [filename] [username]

Lists the other clients.
--------
list

Revokes access to a file for you uploaded
--------
revoke [filename] [username]

Uploads a file to the server.
--------
upload filename

quit"""
INPUT_PROMPT="\nPlease enter a command: (type 'help' for commands)\n"
INVALID_COMMAND="\nPlease supply a valid command."
INVALID_USERNAME="That username contains an invalid syntax. Please user letters and numbers only."
LOGGED_IN="\nLogged in as user {}."
MISSING_ARGS="Missing arguments. Requires server port, connection type and debug flag"
REVOKE_ERROR="\nUnable to revoke access for that user. Ensure all provided values are correct."
RUNNING_TESTS="\nRunning the tests..."
SENDING="Sending: {}"
SENDING_PENDING="Sending the file to the server..."
SERVER_ERROR="Error occurred. Server is closing its connections."
SERVING="Starting server at {}:{}"
TEST_COMPLETED="Test {} was completed successfully."
TEST_ERROR="Test {} failed."
UPLOAD_ERROR="Upload failed for file {} and user {}."