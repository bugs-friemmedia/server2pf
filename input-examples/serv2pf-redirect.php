<?php

# Get the Client IP-Address
$ip = isset($_SERVER['HTTP_CLIENT_IP']) 
    ? $_SERVER['HTTP_CLIENT_IP'] 
    : (isset($_SERVER['HTTP_X_FORWARDED_FOR']) 
      ? $_SERVER['HTTP_X_FORWARDED_FOR'] 
      : $_SERVER['REMOTE_ADDR']);

# Open the Text-File, append the IP-Address and close it again.
$s2pfile = fopen("/tmp/ip-liste.txt", "a");
fwrite($s2pfile, $ip."\n");
fclose($s2pfile);

# Execute the Redirect the the error-Page
echo "<script>location.href='error.html';</script>";

?>
