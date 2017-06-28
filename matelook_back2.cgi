#!/usr/bin/perl -w
# By Nathan Zhen [z5017458], Oct 2016

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;

use File::Basename;


sub main() {
    

    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-medium";
    
    my %cookies = CGI::Cookie->fetch;
    if (defined $cookies{'sithLord'}) {
        $users_first_name = $cookies{'sithLord'}->value;
    }
    
    
    $cgi = CGI->new();
    $user_param = $cgi->param('user');
    
    if (defined param('logout')) {
        my $q = CGI->new;
        my $cookie = $q->cookie (
                -name    => 'sithLord',
                -value   => '',
                -path    => '/',
                -expires => '-1d'
        );
    }
    
    if (defined param('username_input') && defined param('password_input')) {
        check_login();
    } else {
        # print start of HTML ASAP to assist debugging if there is an error in the script
        print page_header();
    
        print page_navbar();



        if ($validated_login == 1) {
            print login_success_page();
        } elsif ($validated_login == -1) {
            print login_no_success_page();
        } elsif (defined param("User_Search_Submit")) {
            print search_results();
        } else {
            print user_page();
        }
        
        
        print page_trailer();
        
    }
    
}

sub check_login {

    # Referenced from: http://www.perlmonks.org/?node_id=513736
    my $username = $cgi->param('username_input');
    my $password = $cgi->param('password_input');
    $validated_login = 0;
    
    # Referenced from: http://stackoverflow.com/questions/2601027/how-can-i-check-if-a-file-exists-in-perl
    if (!-e "accounts.txt") {
        my @user_pass = ();
        foreach my $user_filename (glob("$users_dir/*/user.txt")) {
            $user_filename =~ /\/(.*)\/user\.txt/;
            my $zid_login = $1;
            open my $f, "$user_filename" or die "can not open $user_filename: $!";
            my $pass_login = join '', <$f>;
            
            $pass_login =~ /password\=(.*)\s*/;
            $pass_login = $1;
            push @user_pass, "$zid_login:$pass_login\n";
            close $f;
        }   
        
        open(my $fh, '>', "accounts.txt") or die "Could not open file 'accounts.txt' $!";
        print $fh @user_pass;
        close $fh;
    }
    
    
    open (IN, "accounts.txt") or die;
    while (<IN>) {
        if (/^$username\:$password$/) {
            $validated_login = 1;
            last;
        }
    }
    close(IN);
    
    if(!$validated_login) {
        $validated_login = -1;
        
        print page_header();
        
        print page_navbar();
        
        print login_no_success_page();
        
        print page_trailer();
        
    } else {
        open my $f, "$users_dir/$username/user.txt";
        my $users_f_name = join '', <$f>;
        $users_f_name =~ /full\_name\=(\w+)\s+/;
        $users_first_name = $1;
        
        $logged_in = 1;
        
        my $cgi = CGI->new;
        my $cookie = $cgi->cookie(
            -name  => 'sithLord',
            -value => 'DarthVadar'
        );
        
        print "Set-Cookie: $cookie\n";
        
        print page_header();
        
        print page_navbar();
        
        print login_success_page();
        
        print page_trailer();
    }
    
    return;
}

sub page_navbar {

    my $login_form = "
          <ul class=\"nav navbar-nav navbar-right\">
          <!-- If user is logged in -->
            <li class=\"active\"><a href=\"?user=z5013363\">$users_first_name<span class=\"sr-only\">(current)</span></a></li>
            <li><a href=\"?logout=1\"><span class=\" glyphicon glyphicon-off\" name=\"logout\"></span></a></li>
          </ul>
        ";
    my %cookies = CGI::Cookie->fetch;
#    if (defined $cookies{'sithLord'}) {
#        my $id = $cookies{'sithLord'}->value;
#    }
#    print "<p>$id\n";
    
    if (!defined $cookies{'sithLord'}) {
        $login_form = "
          <form class=\"navbar-form navbar-right\">
            <div class=\"form-group\">
              <input class=\"form-control\" name=\"username_input\" type=\"text\" placeholder=\"zID\">
            </div>
            <div class=\"form-group\">
              <input class=\"form-control\" name=\"password_input\" type=\"password\" placeholder=\"Password\">
            </div>
            <button name=\"login_button\" class=\"btn btn-success\" type=\"submit\">Sign in</button>
          </form>
        ";
    }      
    
    print "
  <body>

    <!-- Fixed navbar -->
    <nav class=\"navbar navbar-inverse navbar-fixed-top\">
      <div class=\"container\">
        <div class=\"navbar-header\">
          <button type=\"button\" class=\"navbar-toggle collapsed\" data-toggle=\"collapsed\" data-target=\"#navbar\" aria-expanded=\"false\" aria-controls=\"navbar\">
            <span class=\"sr-only\">Toggle navigation</span>
            <span class=\"icon-bar\"></span>
            <span class=\"icon-bar\"></span>
            <span class=\"icon-bar\"></span>
          </button>
          <a class=\"navbar-brand\" href=\"./matelook.cgi\">matelook</a>
        </div>
        <div id=\"navbar\" class=\"navbar-collapse collapse\">
          <ul class=\"nav navbar-nav\">
            <li class=\"active\"><a href=\"./matelook.cgi\">Home</a></li>
            
          </ul>
          
          <form class=\"navbar-form navbar-left\" method=\"post\">
            <div class=\"form-group\">
              <input type=\"text\" class=\"form-control\" placeholder=\"Search\" name=\"User_Search_Submit\">
            </div>
            
            <button class=\"btn btn-danger\" type=\"submit\">
              <span class=\" glyphicon glyphicon-search\"></span>
            </button>
          </form>
          $login_form
        </div><!--/.nav-collapse -->
      </div>
    </nav>
    ";
    
    return;
}

sub login_success_page {
    $validated_login = 0;
    
    
    print "<h1>Hi $users_first_name</h1>\n";

#    my %cookies = fetch CGI::Cookie;

#    # print the cookie
#    while (( $k,$v) = each %cookies) {
#       print "<p>$k = $v\n";
#    }
    


    my %cookies = CGI::Cookie->fetch;
    my $id = $cookies{'sithLord'}->value;
    print "<p>$id\n";
    return;
}

sub login_no_success_page {
    $validated_login = 0;
    
    print "<h1>Login failed.</h1>\n";
    
    return;
}

#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    #my $n = param('n') || 0;
    #my @users = sort(glob("$users_dir/*"));
    if (!defined $user_param) {
        $user_to_show  = "$users_dir/z3275760";
    } else {
        $user_to_show = "$users_dir/$user_param";
    }
    
    
    my $details_filename = "$user_to_show/user.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    $details = join '', <$p>;
    
    # We format the details to something readable
    $details = format_details($details);
    
    close $p;
    
    # Profile picture directory
    my $prof_pic_filename = "$user_to_show/profile.jpg";
    # The list of user posts on their page (sorted in reverse chronological order)
    my @posts_list = generate_user_posts();
    # The next user parameter
    #my $next_user = $n + 1;

    # Placeholder image when there is no image javascript from:
    # http://stackoverflow.com/questions/980855/inputting-a-default-image-in-case-the-src-arribute-of-an-html-img-is-not-valid
    return <<eof
<div class="matelook_user_details">
      <div class="matelook_user_image"><img src=\"$prof_pic_filename\" onerror=\"this.src=\'default.gif\'\" /></div>
        $details
      </div>
      <p>
      <div class="matelook_user_posts_bg">
      @posts_list
      </div>
eof
}

sub format_details {
    my ($details) = @_;
    my @details_arr = ();

    push @details_arr, "<div class\= \"user_main_details\">";
    
    # ===== PUBLIC INFORMATION ===== #
    if ($details =~ /full\_name\=(.*)\s*/) {
        my $full_name = "<h1>$1</h1>\n";
        push @details_arr, $full_name;
    }
    if ($details =~ /zid\=(.*)\s*/) {
        my $zid = "zID: $1\n";
        push @details_arr, $zid;
    }
    if ($details =~ /program\=(.*)\s*/) {
        my $program = "Program: $1\n";
        push @details_arr, $program;
    }
    if ($details =~ /birthday\=(.*)\s*/) {
        my $birthday = "Birthday: $1\n";
        push @details_arr, $birthday;
    }
    if ($details =~ /home\_suburb\=(.*)\s*/) {
        my $home_suburb = "From: $1\n";
        push @details_arr, $home_suburb;
    }

    push @details_arr, "        </div>\n";

    if ($details =~ /mates\=(.*)\s*/) {
        my $mates = $1;
        my @mates_arr = split /,/, $mates;
        push @details_arr, "      <div class\= \"mates_list_details\"><br><b>Mates with:</b><br>";
#        push @details_arr, "<div class=\"row\">";
        foreach my $zid (@mates_arr) {
            $zid =~ s/(\[|\]|\,|\s+)//g;
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            my $mate_profile = "<div class=\"mates_list\"><div class=\"user_thumbnail\"><a href=\"?user=$zid\"><img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'default.gif\'\" /></a></div><a href=\"?user=$zid\">$name</a></div>";
#            my $mate_profile = "
#  <div class=\"col-xs-6 col-md-3\">
#    <a href=\"?user=$zid\" class=\"thumbnail\">
#      <img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'default.gif\'\" />
#    </a>
#  </div>";
    
            push @details_arr, $mate_profile;
        }
        push @details_arr, "</div>\n";
        
        
    }
    
    # ===== PRIVATE INFORMATION ===== #
    if ($details =~ /email\=(.*)\s*/) {
        my $email = "Email: $1\n";
        push @details_arr, $email;
    }
    if ($details =~ /password\=(.*)\s*/) {
        my $password = "Password: $1\n";
        push @details_arr, $password;
    }
    if ($details =~ /courses\=(.*)\s*/) {
        my $courses = "Courses: $1\n";
        $courses =~ s/[\[|\]]//g;
        my @courses_arr = split /,/, $courses;
        foreach my $course (@courses_arr) {
            $course =~ s/^\s+|\s+$//;
            $course = "$course, ";
        }
        $courses = join '', @courses_arr;
        $courses =~ s/,\s+$//;
        push @details_arr, $courses;
    }
    if ($details =~ /home\_longitude\=(.*)\s*/) {
        my $home_longitude = "Home longitude: $1\n";
        push @details_arr, $home_longitude;
    }
    if ($details =~ /home\_latitude\=(.*)\s*/) {
        my $home_latitude = "Home latitude: $1\n";
        push @details_arr, $home_latitude;
    }
    
    $f_details = join '', @details_arr;
    return $f_details;
}

sub generate_user_posts {
    #my $n = param('n') || 0;
    #my @users = sort(glob("$users_dir/*"));
    if (!defined $user_param) {
        $user_to_show  = "$users_dir/z3275760";
    } else {
        $user_to_show = "$users_dir/$user_param";
    }

    # Iterates through the posts
    # Modified from Wk11 Tutorial given code
    my %post_hash = ();
    my $folder_num = 0;
    my @posts_arr = ();
    foreach my $post_filename (glob("$user_to_show/posts/*/post.txt")) {
        $post_filename =~ /posts\/(.*)\/post\.txt/;
        $folder_num = $1;
        open my $f, "$post_filename" or die "can not open $post_filename: $!";
        $file_time = join '', <$f>;
        $file_time =~ /time\=(.*)\s*/;
        $file_time = $1;
        $post_hash{$file_time} = $folder_num;
        close $f;
    }
    foreach $file_time (reverse sort keys %post_hash) {
        #printf "%-8s %s<br>\n", $file_time, $post_hash{$file_time};
        open $posts_file, "$user_to_show/posts/$post_hash{$file_time}/post.txt" or die "can not open $user_to_show/posts/$post_hash{$file_time}/post.txt: $!";
        $posts_file_contents = join ' ', <$posts_file>;
        $posts_file_contents =~ s/\n/\<br\>\n/g;
        $posts_file_contents .= "<br>\n";
        push @posts_arr, $posts_file_contents;
    }
    
    close $posts_file;
    my @formatted_posts = format_user_post(@posts_arr);
    return @formatted_posts;

}

# Formats the user posts to a consistent form.
sub format_user_post {

    # The array of posts before formatting
    my (@old_posts_arr) = @_;
    # The array of posts after formatting
    my $posts_arr = ();
    
    
    # Goes through each post and formats it
    foreach my $posts (@old_posts_arr) {
        # Separates each post with div
        push @posts_arr, "\<div class\=\"matelook_user_posts\"\>\n";
        
        # Regex to format post
        if ($posts =~ /from\=(.*)\s*/) {
            my $from = "From: $1\n";
            push @posts_arr, $from;
        }
        if ($posts =~ /time\=(.*)\s*/) {
            my $time = "Time: $1\n";
            push @posts_arr, $time;
        }
        if ($posts =~ /message\=(.*)\s*/) {
            my $message = "<p>$1\n</p>";
            $message =~ s/\\n/<br>/g;
            push @posts_arr, $message;
        }
        if ($posts =~ /longitude\=(.*)\s*/) {
            my $longitude = "Longitude: $1\n";
            push @posts_arr, $longitude;
        }
        if ($posts =~ /latitude\=(.*)\s*/) {
            my $latitude = "Latitude: $1\n";
            push @posts_arr, $latitude;
        }
        
        # Adds a break between each post (with each post separated by div)
        push @posts_arr, "</div>";
    }
    return @posts_arr;
}

sub search_results {

    my $search = param("User_Search_Submit");    
    # Sanitize search results
    # Referenced from http://staff.washington.edu/tabrooks/533.course/cgi/cgi_metacharacters.html
    my $OK_CHARS='-a-zA-Z0-9_.@\s';
    $search =~ s/[^$OK_CHARS]/_/go;
    
    my $search_header = "<h1>Search results for: \"$search\"</h1>
                           <br><br>
                         <div class=\"row\">";
    
    my $search_zid = 0;
    my $search_line = "";
    
    
    my @search_results_list = ();
    
    
    foreach my $user_filename (glob("$users_dir/*/user.txt")) {
        my @search_details_arr = ();
        my $search_name = "";
        
        $user_filename =~ /\/(.*)\/user\.txt/;
        $search_zid = $1;
        open my $f, "$user_filename" or die "can not open $user_filename: $!";
        $search_line = join '', <$f>;
        if ($search_line =~ /full_name\=(.*)\s*/) {
            $search_name = $1;
        }
   
        
        
        if ($search_line =~ /zid\=(.*)\s*/) {
            my $zid = "zID: $1<br>\n";
            push @search_details_arr, $zid;
        }
        if ($search_line =~ /program\=(.*)\s*/) {
            my $program = "Program: $1<br>\n";
            push @search_details_arr, $program;
        }
        if ($search_line =~ /home\_suburb\=(.*)\s*/) {
            my $home_suburb = "From: $1<br>\n";
            push @search_details_arr, $home_suburb;
        }
        
        
        
        if ($search_name =~ /$search/i) {
            my $search_box = "
      <div class=\"col-sm-6 col-md-4\">
        <div class=\"thumbnail\">
            <a href=\"?user=$search_zid\">
            <img src=\"$users_dir/$search_zid/profile.jpg\" onerror=\"this.src=\'default.gif\'\" />
            </a>
          <div class=\"caption\">
            <h3><a href=\"?user=$search_zid\">$search_name</a></h3>
            <p>@search_details_arr</p>
            <p><a href=\"#\" class=\"btn btn-primary\" role=\"button\">Add Mate</a><a href=\"?user=$search_zid\" class=\"btn btn-default\" role=\"button\">View Profile</a></p>
          </div>
        </div>
      </div>";
            push @search_results_list, $search_box;
        }
        
        close $f;
    }
    
    
    
    return <<eof
    $search_header
    @search_results_list
    </div> 
eof
}

#
# HTML placed at the top of every page
#
sub page_header {
    return <<eof
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">

    <title>matelook</title>

    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="matelook.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <script src="js/ie-emulation-modes-warning.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  
eof
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    #return $html;
    
    return <<eof
    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script>window.jQuery || document.write(\'<script src=\"js/vendor/jquery.min.js\"><\\/script>\')</script>
    <script src="js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="assets/js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>
    
eof
}


main();
