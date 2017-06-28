#!/usr/bin/perl

use CGI;
use CGI::Cookie;


$q = new CGI;

# Create a new cookie
$cookie = new CGI::Cookie(-name=>'CookieName',-value=>'CookieValue');

# set the Cookie
print $q->header(-cookie=>$cookie);

    
print $q->start_html;


%cookies = fetch CGI::Cookie;

# print the cookie
while (( $k,$v) = each %cookies) {
   print "<p>$k = $v";
}


print $q->end_html;
exit;