#!/usr/bin/perl -w
# By Nathan Zhen [z5017458], Oct 2016
# Uses Bootstrap as a front-end framework

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Session;

use File::Basename;

#
# Main function
#
sub main() {
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
    #
    # define some global variables
    #

    # Global variable for the directory with all the user files
    $users_dir = "dataset-medium";
    
    # This variable is used when comments need to be shown/hidden
    $unique_comment_id = 0;

    # CGI::Session tutorial 
    # http://search.cpan.org/~markstos/CGI-Session-4.43/lib/CGI/Session/Tutorial.pm
    $session = CGI::Session->load() or die CGI::Session->errstr;
    
    # This variable allows us to address the user by their first name
    $users_first_name = $session->param('first_name');
    
    # We use this param to navigate between user pages
    $cgi = CGI->new();
    $user_param = $cgi->param('user') || $session->param('username');
    

    # If the user presses the logout button
    if ($cgi->param('logout')) {
        # We delete the session
        $session->delete();
        $session->flush();
    }


    #
    # Load the correct pages
    #
    
    # If user enters a username and/or password
    if (defined param('username_input') && defined param('password_input')) {
        # Subroutine to check the login
        check_login();
    } else {
        # print start of HTML ASAP to assist debugging if there is an error in the script
        print page_header();
        
        # Prints the navigation bar at the top of every page
        print page_navbar();

        # If the user enters a search
        if (defined param("User_Search_Submit")) {
            print search_results();
        # If the user wants their newsfeed (by clicking the home button)
        } elsif (defined param("home") && $session->param('username')) {
            print news_feed();
        # Shows a user's page
        } elsif ($session->param('username')) {
            print user_page();
        # Else the user is not logged in
        } else {
            print guest_page();
        }
        
        # Page trailer at the end of every page
        print page_trailer();
        
    }
    
}

#
# Function is called when user logs in
# Referenced from: 
# http://www.perlmonks.org/?node_id=513736
#
sub check_login {

    # Take the username and passwords that were entered into the login form
    my $username = $cgi->param('username_input');
    my $password = $cgi->param('password_input');
    
    # Flag which activates once when login is validated
    $validated_login = 0;
    
    # Referenced from: 
    # http://stackoverflow.com/questions/2601027/how-can-i-check-if-a-file-exists-in-perl
    # If the accounts.txt file doesn't exist, we create it
    if (!-e "accounts.txt") {
        
        # Array to store usernames and password combos
        my @user_pass = ();
        # Traverse through the $users_dir and looks for user.txt (for each zID)
        foreach my $user_filename (glob("$users_dir/*/user.txt")) {
            # Saves the filename for each zID
            $user_filename =~ /\/(.*)\/user\.txt/;
            # Saves the zID
            my $zid_login = $1;
            # Open the file containing their user information
            open my $f, "$user_filename" or die "can not open $user_filename: $!";
            # Create a string with the entire file
            my $pass_login = join '', <$f>;
            
            # Save the password
            $pass_login =~ /password\=(.*)\s*/;
            $pass_login = $1;
            # Push the password to the username:password array
            push @user_pass, "$zid_login:$pass_login\n";
            close $f;
        }   
        
        # Create the accounts.txt file and print the array of username:password into it
        open(my $fh, '>', "accounts.txt") or die "Could not open file 'accounts.txt' $!";
        print $fh @user_pass;
        close $fh;
    }
    
    # Open accounts.txt and look for the username:password combo
    open (IN, "accounts.txt") or die;
    while (<IN>) {
        if (/^$username\:$password$/) {
            $validated_login = 1;
            last;
        }
    }
    close(IN);
    
    # If the combo does not exist
    if(!$validated_login) {
        
        print page_header();
        
        print page_navbar();
        
        print login_no_success_page();
        
        print page_trailer();

    # Else the combo exists
    } else {
        # Open user.txt of the corresponding zID and find their first name
        open my $f, "$users_dir/$username/user.txt";
        my $users_f_name = join '', <$f>;
        $users_f_name =~ /full\_name\=(\w+)\s+/;
        $users_first_name = $1;
        
        # Create a new "session" aka cookie using CGI::Session
        $session = CGI::Session->new() or die CGI::Session->errstr;
        
        # Print this session to the header, before "Content-Type: text/html"
        print $session->header();
        
        # Save these parameters to the cookie
        $session->param('username', $username);
        $session->param('first_name', $users_first_name);
        $session->flush();
        #$session->expire('+1M');    # expire after a month and so on.
        
        # Set the flag to remove "Content-Type: text/html", since the header() adds it
        $remove_content_header = 1;
        
        # We manually print out the newsfeed straight after logging in
        print page_header();
        
        print page_navbar();
        
        print news_feed();
        
        print page_trailer();
    }
    
    return;
}

#
# Prints the navigation bar for each page
#
sub page_navbar {
    
    # This variable allows us to go to the user's page when they click their own name on the navbar
    my $user_url = $session->param('username');
    
    # The search bar is only visible when the user is logged in
    my $search_bar = "
        <div class=\"form-group\">
              <input type=\"text\" class=\"form-control\" placeholder=\"Search\" name=\"User_Search_Submit\">
            </div>
            
            <button class=\"btn btn-danger\" type=\"submit\">
              <span class=\" glyphicon glyphicon-search\"></span>
            </button>
    ";
    if (!defined $session->param('username')) {
        $search_bar = "";
    }

    # The variable $login_form changes depending on whether the user is logged in or not
    # If logged in, then it will display their first name and a log out button
    my $login_form = "
          <ul class=\"nav navbar-nav navbar-right\">
          <!-- If user is logged in -->
            <li class=\"active\"><a href=\"?user=$user_url\">$users_first_name<span class=\"sr-only\">(current)</span></a></li>
            <li><a href=\"?logout=1\"><span class=\" glyphicon glyphicon-off\" name=\"logout\"></span></a></li>
          </ul>
        ";

    # If not logged in, it will display a login form for username and password
    if (!defined $session->param('username')) {
        $login_form = "
          <form class=\"navbar-form navbar-right\" method=\"post\">
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
    
    # This prints the entire navbar
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
          <a class=\"navbar-brand\" href=\"?home=1\">matelook</a>
        </div>
        <div id=\"navbar\" class=\"navbar-collapse collapse\">
          <ul class=\"nav navbar-nav\">
            <li class=\"active\"><a href=\"?home=1\">Home</a></li>
            
          </ul>
          
          <form class=\"navbar-form navbar-left\" method=\"get\">
            $search_bar
          </form>
          $login_form
        </div><!--/.nav-collapse -->
      </div>
    </nav>
    ";
    
    return;
}

#
# This page is shown when the user is not logged in
#
sub guest_page {

    print "
    <!-- Header -->
    <a name=\"about\"></a>
    <div class=\"intro-header\">
 
                    <div class=\"intro-message\">
                        <h1>matelook</h1>
                        <h3>It's like Facebook, but for famous people</h3>
                        <hr class=\"intro-divider\">
                    </div>
    </div>
    <!-- /.intro-header -->
    ";

    return;
}

#
# On successful login, this page is displayed
#
sub news_feed {

    $validated_login = 0;
        
    print "<center><h1>Hi $users_first_name<br>\n<br>\n</h1></center>\n";
    
    # Takes the param and puts it the $zid variable    
    my $zid = $session->param('username');
    $user_param = $zid;
    
    # @newsfeed_arr stores all the posts (unsorted)
    # %news_posts sorts the posts with most recent first and prints it
    my @newsfeed_arr = ();
    my %news_posts = ();
    

    $user_to_show = "$users_dir/$zid";
    
    # Grab the user's friends and send all their posts to the main array
    my $details_filename = "$user_to_show/user.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    my $details = join '', <$p>;
    if ($details =~ /mates\=(.*)\s*/) {
    
        my $mates = $1;
        my @mates_arr = split /,/, $mates;

        foreach my $mate_zid (@mates_arr) {
            $mate_zid =~ s/(\[|\]|\,|\s+)//g;
            
            my @friends_post_list = generate_user_posts($mate_zid);
            push @newsfeed_arr, @friends_post_list;
        }
              
    }
    close $p;
    
    # Generate the user's posts and push it to the main array
    my @posts_list = generate_user_posts();
    push @newsfeed_arr, @posts_list;
    
    # For every post that the user is mentioned in (z5555555), push to main array
    foreach my $post_filename (glob("$users_dir/*/posts/*/post.txt")) {
        $post_filename =~ /\/(.*)\/posts\/(.*)\/post\.txt/;
        my $user_post_zid = $1;
        my $folder_num = $2;
       
        open my $f, "$post_filename" or die "can not open $post_filename: $!";
        my $tagged = join '', <$f>;
        # If there is a match
        if ($tagged =~ /message\=.*$user_param.*/) {
            my @generated_post = generate_single_post($user_post_zid, $folder_num);
            push @newsfeed_arr, @generated_post;
        }
        close $f;
    }
    
    # For every comment the user is mentioned in
    foreach my $comment_filename (glob("$users_dir/*/posts/*/comments/*/comment.txt")) {
        $comment_filename =~ /\/(.*)\/posts\/(.*)\/comments/;
        my $user_post_zid = $1;
        my $folder_num = $2;
        
        open my $f, "$comment_filename" or die "can not open $comment_filename: $!";
        my $tagged = join '', <$f>;
        # If there is a match
        if ($tagged =~ /message\=.*$user_param.*/) {
            my @generated_post = generate_single_post($user_post_zid, $folder_num);
            push @newsfeed_arr, @generated_post;
        }
        close $f;
    }
    
    # We fix the timestamp for each post to eg. 03 October 2015 
    # or 13 September (we remove 2016 if the post is from 2016)
    foreach my $newsfeed_post (@newsfeed_arr) {
        
        # $post_time is used for the hash to sort our posts by time
        my $post_time = "";
        $newsfeed_post =~ /\"post_op\".*\=\"timestamp\"\>(.*)\<\/div\>/;
        $post_time = $1;
        $post_time =~ s/\<br\>//g;

        # $fixed_time contains the fixed timestamp
        my $fixed_time = fix_timestamp($post_time);
        # $post_time2 is used to fix regex issues present in $post_time
        my $post_time2 = $post_time;
        $post_time2 =~ s/\:/\\:/g;
        $post_time2 =~ s/\-/\\-/g;
        $post_time2 =~ s/\+/\\+/g;
        $fixed_time =~ s/\<div class \=\"timestamp\"\>//;
        $fixed_time =~ s/\<\/div\>//;
        $newsfeed_post =~ s/$post_time2/$fixed_time/gi;

        # Hashing avoids duplicates and sorts our posts based on time
        $news_posts{$post_time} = $newsfeed_post;
    }
    
    # Now we sort in reverse chronological order
    foreach my $post_time (reverse sort keys %news_posts) {
        # Create a new div for each post
        print "<div class=\"matelook_user_posts_bg\">\n";
        print $news_posts{$post_time};
        print "</div>\n";

    }
    return;
}

#
# When login fails, this page is displayed
#
sub login_no_success_page {

    $validated_login = 0;
    
    # The hint contains a working username/password combo
    print "<h1>Login failed.</h1>\n";
    print "<p>Incorrect username/password. Try again.\n";
    print "<p><font color=\'#EEEEEE\'>Hint: try z3466413 and nicole</font><br><br><br><br>\n";
    
    return;
}

#
# Shows the user's personal page
#
sub user_page {
    
    # The default page to show is James Franco's
    # Used mainly for testing purposes
    if (!defined $user_param) { 
        $user_to_show  = "$users_dir/z3466413";
    # Else, show the corresponding user's page we requested
    } else {
        $user_to_show = "$users_dir/$user_param";
    }
    
    # This variable is the filename with the user details
    my $details_filename = "$user_to_show/user.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    # Create a string with the entire details file
    $details = join '', <$p>;
    
    # We format the details to something readable
    $details = format_details($details);
    
    close $p;
    
    # Profile picture directory
    my $prof_pic_filename = "$user_to_show/profile.jpg";
    # The list of user posts on their page (sorted in reverse chronological order)
    my @posts_list = generate_user_posts();

    # Same thing as above, which fixes timestamps on posts
    foreach my $user_post (@posts_list) {
        my $post_time = "";
        $user_post =~ /\"post_op\".*\=\"timestamp\"\>(.*)\<\/div\>/;
        $post_time = $1;
        $post_time =~ s/\<br\>//g;
        
        my $fixed_time = fix_timestamp($post_time);
        
        my $post_time2 = $post_time;
        $post_time2 =~ s/\:/\\:/g;
        $post_time2 =~ s/\-/\\-/g;
        $post_time2 =~ s/\+/\\+/g;
        
        $fixed_time =~ s/\<div class \=\"timestamp\"\>//;
        $fixed_time =~ s/\<\/div\>//;

        $user_post =~ s/$post_time2/$fixed_time/gi;
    }


    # Placeholder image when there is no image javascript referenced from:
    # http://stackoverflow.com/questions/980855/inputting-a-default-image-in-case-the-src-arribute-of-an-html-img-is-not-valid
    
    # Returns the user's entire page
    return <<eof
<div class="matelook_user_details">
      <div class="matelook_user_image"><img src=\"$prof_pic_filename\" onerror=\"this.src=\'images/default.gif\'\" /></div>
        $details</div>
      <p>
      <div class="matelook_user_posts_bg">
      @posts_list
      </div>
eof
}


#
# Formats the user's details to a readable format
#
sub format_details {
    # Using the string that contains the entire user.txt file
    my ($details) = @_;
    my @details_arr = ();
    
    # Formats this section of the user's page
    push @details_arr, "<div class\= \"user_main_details\">";
    
    # ===== PUBLIC INFORMATION ===== #
    # Finds the corresponding regex, formats it and pushes it to the final array
    if ($details =~ /full\_name\=(.*)\s*/) {
        my $full_name = "<div class=\"matelook_heading\">$1</div>\n";
        push @details_arr, $full_name;
    }
    if ($details =~ /zid\=(.*)\s*/) {
        my $zid = "<font color=\'#999999\'>zID</font> $1\n";
        push @details_arr, $zid;
    }
    if ($details =~ /program\=(.*)\s*/) {
        my $program = "<font color=\'#999999\'>Studies</font> $1\n";
        push @details_arr, $program;
    }
    if ($details =~ /home\_suburb\=(.*)\s*/) {
        my $home_suburb = "<font color=\'#999999\'>From</font> $1\n";
        push @details_arr, $home_suburb;
    }
    if ($details =~ /birthday\=(.*)\s*/) {
        my $old_birthday = $1;
        $old_birthday =~ /(.*)\-(.*)\-(.*)/;
        my $new_birthday = "$3/$2/$1";
        my $birthday = "<font color=\'#999999\'>Birthday</font> $new_birthday\n";
        push @details_arr, $birthday;
    }
    
    # Splits up this section with the mates list section
    push @details_arr, "        </div>\n";

    # Creates the mates list
    if ($details =~ /mates\=(.*)\s*/) {
    
        # Splits the string that contains all mates into an array
        my $mates = $1;
        my @mates_arr = split /,/, $mates;
        push @details_arr, "      <div class\= \"mates_list_details\"><br><font color=\'#999999\'>Mates with</font><br>";

        # For each person in this array, we take their thumbnail and name
        foreach my $zid (@mates_arr) {
        
            # Remove unwanted characters
            $zid =~ s/(\[|\]|\,|\s+)//g;
            # Open up their user.txt to find their full name
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            # Puts together their thumbnail and full name
            my $mate_profile = "<div class=\"mates_list\"><div class=\"user_thumbnail\"><a href=\"?user=$zid\"><img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'images/default.gif\'\" /></a></div><a href=\"?user=$zid\"><b>$name</b></a></div>";
            # Push this to the final array for their details
            push @details_arr, $mate_profile;
        }
        
        # Ends the mates list section
        push @details_arr, "</div>\n";
        
        
    }
    
    # ===== PRIVATE INFORMATION ===== #
    # Commented out the push to details_arr so these are hidden.
    if ($details =~ /email\=(.*)\s*/) {
        my $email = "Email: $1\n";
        #push @details_arr, $email;
    }
    if ($details =~ /password\=(.*)\s*/) {
        my $password = "Password: $1\n";
        #push @details_arr, $password;
    }
    
    # Removes unwanted symbols and formats the courses into a readable format
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
        #push @details_arr, $courses;
    }
    if ($details =~ /home\_longitude\=(.*)\s*/) {
        my $home_longitude = "Home longitude: $1\n";
        #push @details_arr, $home_longitude;
    }
    if ($details =~ /home\_latitude\=(.*)\s*/) {
        my $home_latitude = "Home latitude: $1\n";
        #push @details_arr, $home_latitude;
    }
    
    # Put everything in the array together into a string and return it    
    my $f_details = join '', @details_arr;
    return $f_details;
}

#
# Generates the user's posts
#
sub generate_user_posts {
    
    # Default behaviour
    if (!defined $user_param) {
        $user_to_show  = "$users_dir/z3466413";
    } else {
        $user_to_show = "$users_dir/$user_param";
    }
    
    my ($zid_check) = @_;
    
    if ($zid_check =~ /(z[0-9]{7})/) {
        my $fix_zid = @_;
        $fix_zid =~ s/\s+//g;
        $user_to_show = "$users_dir/@_"; 
    }

    # Iterates through the posts
    # Modified from Wk11 Tutorial given code
    # *******************
    # This was done before Andrew fixed up the dataset to be in 
    # chronological order based on the folder number. At the time, 
    # the folder numbers didn't have any relation to the time, hence I 
    # had to rearrange the posts, which I have done below
    # *******************
    my %post_hash = ();
    my $folder_num = 0;
    my @posts_arr = ();
    
    # This variable is used for printing comments
    $comment_folder_num = -1;

    # For each folder (0,1,2,etc.), we find its time and hash it based 
    # on its time, with the hash value being its folder number
    foreach my $post_filename (glob("$user_to_show/posts/*/post.txt")) {
        $post_filename =~ /posts\/(.*)\/post\.txt/;
        $folder_num = $1;
        
        open my $f, "$post_filename" or die "can not open $post_filename: $!";
        $file_time = join '', <$f>;
        $file_time =~ /time\=(.*)\s*/;
        $file_time = $1;
        $post_hash{$file_time} = $folder_num;
        $comment_folder_num++;
        close $f;
    }
    
    # Now we sort the hash in reverse chronological order
    foreach $file_time (reverse sort keys %post_hash) {

        # Now we can use the hash value (the folder number) to show the most recent posts
        open my $posts_file, "$user_to_show/posts/$post_hash{$file_time}/post.txt" or die "can not open $user_to_show/posts/$post_hash{$file_time}/post.txt: $!";
        # We put the post into a string and push it to the array.
        my $posts_file_contents = join '', <$posts_file>;
        $posts_file_contents =~ s/\n/\<br\>\n/g;
        push @posts_arr, $posts_file_contents;
        close $posts_file;
    }
    
    
    # Send the array off to be formatted
    my @formatted_posts = format_user_post(@posts_arr);
    return @formatted_posts;

}

#
# Generates a single post instead of all the user's posts. 
# Used in the newsfeed to find posts that the user is mentioned in.
#
sub generate_single_post {
    
    my @single_post = ();

    # Flag for adding a "you were mentioned here" before the post
    $mentioned = 1;
    # Flag to fix folder finding
    $is_single_post = 1;
    
    # Variables passed into this function
    my ($post_zid, $folder_num) = @_;
    
    $user_to_show = "$users_dir/$post_zid"; 
    
    # Global variable for fix folder finding
    $comment_folder_num = $folder_num;

    # Grab the post content
    open my $posts_file, "$users_dir/$post_zid/posts/$folder_num/post.txt" or die;
    my $posts_file_contents = join '', <$posts_file>;
    $posts_file_contents =~ s/\n/\<br\>\n/g;
    push @single_post, $posts_file_contents;    
    close $posts_file;

    # Send the array off to be formatted
    @single_post = format_user_post(@single_post);
    
    $mentioned = 0;
    $is_single_post = 0;

    return @single_post;

   
}


#
# Formats the user posts to a consistent form.
#
sub format_user_post {

    # The array of posts before formatting
    my (@old_posts_arr) = @_;
    # The array of posts after formatting
    my @user_posts_arr = ();
    
    # We take this variable from generate_user_posts() to find the highest folder number
    # so we can find the comment for the most recent post and work our way backwards
    # This is so the comments match up with the posts being generated
    my $folder_num = $comment_folder_num;
    
    # Goes through each post and formats it
    foreach my $posts (@old_posts_arr) {
        my @posts_arr = ();
        
        # Adds some pretext if flag is set
        if ($mentioned) {
            push @posts_arr, "<div class=\"mentioned_here\"><i>You were mentioned here.</i></div>\n";
        }

        # Separates each post with div
        push @posts_arr, "\<div class\=\"matelook_user_posts\"\>\n";

        # Regex to format post
        if ($posts =~ /from\=(.*)\s*/) {
            # Remove unwanted characters
            my $zid = $1;
            $zid =~ s/\<br\>//g;
            # Open up their user.txt to find their full name
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            # Puts together their thumbnail and full name
            my $post_profile = "<div class=\"post_op\"><div class=\"user_thumbnail\"><a href=\"?user=$zid\"><img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'images/default.gif\'\" /></a></div><a href=\"?user=$zid\"><b>$name</b></a></div><br>";
            # Push this to the final array for their details
            push @posts_arr, $post_profile;
        }

        if ($posts =~ /time\=(.*)\s*/) {
            my $time = $1;
            $time = "<div class=\"timestamp\">$time</div>";       
            push @posts_arr, $time;
        }

        # If a user is mentioned, their name will come up instead of their
        # zID and it will be a link to their user page
        if ($posts =~ /message\=(.*)\s*/) {            
            my $message = $1;
            if ($message =~ /(z[0-9]{7})/) {
                my $fixed_message = "";
                my @arr = split / /, $message;
                foreach my $line (@arr) {
                    if ($line =~ /(z[0-9]{7})/) {
                        $zid = $1;
                        # Open up their user.txt to find their full name
                        open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
                        my $name = join '', <$file>;
                        $name =~ /full\_name\=(.*)\s*/;
                        $name = $1;
                        $name = "<a href=\"?user=$zid\">$name</a>";
                        $fixed_message .= "$name ";
                    } else {
                        $fixed_message .= "$line ";
                    }
                }
                $fixed_message =~ s/\s+$//;
                $message = $fixed_message;
            }
            $message = "<p>$message\n</p>";
            $message =~ s/\\n/<br>/g;
            push @posts_arr, $message;
        }
        
        # Creates the comments and reply threads below the posts
        my @comments_arr = user_post_comments($folder_num);
        # If it is not a single post, we can iterate through the folders
        if ($is_single_post != 1) {
            $folder_num--;
        }
        push @posts_arr, @comments_arr;
        
        # Adds a break between each post (with each post separated by div)
        push @posts_arr, "</div>\n";
        
        # We push the comments and replies to the single post
        my $single_user_post = join "", @posts_arr;
        push @user_posts_arr, $single_user_post;
    }
    return @user_posts_arr;
}


#
# Generates comments below posts
#
sub user_post_comments {
    my ($folder_num) = @_;
    my @comments_arr = ();
    my $comment_num = 0;
    my $comment_file_exists = 0;

    # If no comment exists, we don't print the show/hide button
    if (-e "$user_to_show/posts/$folder_num/comments/0/comment.txt") {
        # Flag is used to determine if there are comments
        $comment_file_exists = 1;
        push @comments_arr, "
            <div align=\"right\"><font size=\"1\"><a href=\"javascript:showhide(\'comments_bg_$unique_comment_id\')\">
                Click to show/hide comments
            </a></font></div>\n";
        push @comments_arr, "<div id=\"comments_bg_$unique_comment_id\" style=\"display\:none;\" bgcolor=\"\#E6E6FA\">\n";
        # We make every comment unique so that the javascript will show/hide the correct comment
        $unique_comment_id++;
    }

    # Exactly the same as the format_user_post section
    foreach my $comment_file (glob("$user_to_show/posts/$folder_num/comments/*/comment.txt")) {

        # Separates each comment with div
        push @comments_arr, "\<div class\=\"matelook_user_comments\"\>\n";
        
        open my $f, "$comment_file" or die "can not open $comment_file: $!";
        # We put the post into a string and push it to the array.
        my $comment_file_contents = join '', <$f>;
        $comment_file_contents =~ s/\n/\<br\>\n/g;
        $comment_file_contents .= "<br>\n";
        
        
        # Regex to format post
        if ($comment_file_contents =~ /from\=(.*)\s*/) {
            # Remove unwanted characters
            my $zid = $1;
            $zid =~ s/\<br\>//g;
            # Open up their user.txt to find their full name
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            # Puts together their thumbnail and full name
            my $comment_profile = "<div class=\"post_comment\"><div class=\"user_thumbnail_comment\"><a href=\"?user=$zid\"><img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'images/default.gif\'\" /></a></div><a href=\"?user=$zid\"><b>$name</b></a></div><br>";
            # Push this to the final array for their details
            push @comments_arr, $comment_profile;
        }
        if ($comment_file_contents =~ /time\=(.*)\s*/) {
            my $time = $1;
            $time = fix_timestamp($time);   
            push @comments_arr, $time;
        }
        if ($comment_file_contents =~ /message\=(.*)\s*/) {
            my $message = $1;
            if ($message =~ /(z[0-9]{7})/) {
                my $fixed_message = "";
                my @arr = split / /, $message;
                foreach my $line (@arr) {
                    if ($line =~ /(z[0-9]{7})/) {
                        $zid = $1;
                        # Open up their user.txt to find their full name
                        open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
                        my $name = join '', <$file>;
                        $name =~ /full\_name\=(.*)\s*/;
                        $name = $1;
                        $name = "<a href=\"?user=$zid\">$name</a>";
                        $fixed_message .= "$name ";
                    } else {
                        $fixed_message .= "$line ";
                    }
                }
                $fixed_message =~ s/\s+$//;
                $message = $fixed_message;
            }
            $message = "$message\n";
            $message =~ s/\\n/<br>/g;
            push @comments_arr, $message;
        }
        # Creates the comments and reply threads below the posts
        my @replies_arr = user_comment_replies($folder_num, $comment_num);
        push @comments_arr, @replies_arr;
        
        
        # Adds a break between each post (with each post separated by div)
        push @comments_arr, "</div>\n";
        $comment_num++;
    }
    if ($comment_file_exists == 1) {
        push @comments_arr, "</div>\n";
    }

    return @comments_arr;
}

#
# Replies below comments
#
sub user_comment_replies {
    my ($folder_num, $comment_num) = @_;
    my @replies_arr = ();
    
    foreach my $replies_file (glob("$user_to_show/posts/$folder_num/comments/$comment_num/replies/*/reply.txt")) {
        # Separates each comment with div
        push @replies_arr, "\<div class\=\"matelook_user_replies\"\>\n";
        
        open my $f, "$replies_file" or die "can not open $replies_file: $!";
        # We put the post into a string and push it to the array.
        my $replies_file_contents = join '', <$f>;
        $replies_file_contents =~ s/\n/\<br\>\n/g;
        $replies_file_contents .= "<br>\n";
        
        
        # Regex to format post
        if ($replies_file_contents =~ /from\=(.*)\s*/) {
            # Remove unwanted characters
            my $zid = $1;
            $zid =~ s/\<br\>//g;
            # Open up their user.txt to find their full name
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            # Puts together their thumbnail and full name
            my $replies_profile = "<div class=\"post_comment\"><div class=\"user_thumbnail_comment\"><a href=\"?user=$zid\"><img src=\"$users_dir/$zid/profile.jpg\" onerror=\"this.src=\'images/default.gif\'\" /></a></div><a href=\"?user=$zid\"><b>$name</b></a></div><br>";
            # Push this to the final array for their details
            push @replies_arr, $replies_profile;
        }
        if ($replies_file_contents =~ /time\=(.*)\s*/) {
            my $time = $1;
            $time = fix_timestamp($time);   
            push @replies_arr, $time;
        }
        if ($replies_file_contents =~ /message\=(.*)\s*/) {
            my $message = $1;
            if ($message =~ /(z[0-9]{7})/) {
                my $fixed_message = "";
                my @arr = split / /, $message;
                foreach my $line (@arr) {
                    if ($line =~ /(z[0-9]{7})/) {
                        $zid = $1;
                        # Open up their user.txt to find their full name
                        open my $file, "$users_dir/$zid/user.txt" or die "can not open $users_dir/$zid/user.txt: $!";
                        my $name = join '', <$file>;
                        $name =~ /full\_name\=(.*)\s*/;
                        $name = $1;
                        $name = "<a href=\"?user=$zid\">$name</a>";
                        $fixed_message .= "$name ";
                    } else {
                        $fixed_message .= "$line ";
                    }
                }
                $fixed_message =~ s/\s+$//;
                $message = $fixed_message;
            }
            $message = "$message\n";
            $message =~ s/\\n/<br>/g;
            push @replies_arr, $message;
        }
        
        # Adds a break between each post (with each post separated by div)
        push @replies_arr, "</div>\n";
    }
    
    return @replies_arr;
}   

#
# Fixes timestamps to a human friendly format
#
sub fix_timestamp {

    # Pass in the original timestamp
    my ($old_time) = @_;
    
    # Timestamp is split into the date and time
    $old_time =~ /(.*)T(.*)\+/;
    my $date = $1;
    my $new_time = $2;
    
    # For the date, we change the month first
    $date =~ /(\d+)\-(\d+)\-(\d+)/;
    my $month = $2;
    
    # If each month
    if ($month == '01') {
        $month = "January" 
    } elsif ($month == '02') {
        $month = "February";
    } elsif ($month == '03') {
        $month = "March";
    } elsif ($month == '04') {
        $month = "April";
    } elsif ($month == '05') {
        $month = "May";
    } elsif ($month == '06') {
        $month = "June";
    } elsif ($month == '07') {
        $month = "July";
    } elsif ($month == '08') {
        $month = "August";
    } elsif ($month == '09') {
        $month = "September";
    } elsif ($month == '10') {
        $month = "October";
    } elsif ($month == '11') {
        $month = "November";
    } elsif ($month == '12') {
        $month = "December";
    } 
    
    # The date is now fixed (eg. 04 October 2015)
    $date = "$3 $month $1";
    
    # If the year is 2016, we drop the year from the timestamp (eg. 14 September if it was 2016-09-14)
    if ($1 == 2016) {
        $date = "$3 $month";
    }
    
    # Also fix the time
    $new_time =~ /(\d+):(\d+)/;
    $new_time = "$1:$2";
    
    return "<div class =\"timestamp\">$date at $new_time</div>"; 
}

#
# Creates the search results page
#
sub search_results {
    
    # Grabs the user's search query
    my $search = param("User_Search_Submit");    
    
    # Sanitize search results
    # Referenced from:
    # http://staff.washington.edu/tabrooks/533.course/cgi/cgi_metacharacters.html
    my $OK_CHARS='-a-zA-Z0-9_.@\s';
    $search =~ s/[^$OK_CHARS]/_/go;
    
    # Formatted search heading
    my $search_heading = "<h1>Search results for: \"$search\"</h1>
                           <br><br>
                         <div class=\"row\">";
    # Initialise
    my $search_zid = 0;
    my $search_line = "";
    my @search_results_list = ();
        
    # Search through the directory of users
    foreach my $user_filename (glob("$users_dir/*/user.txt")) {
        # For each user, we create an array for their details and a var for their name
        my @search_details_arr = ();
        my $search_name = "";
        
        # We open up their file to see if they match the query
        $user_filename =~ /\/(.*)\/user\.txt/;
        $search_zid = $1;
        open my $f, "$user_filename" or die "can not open $user_filename: $!";
        $search_line = join '', <$f>;
        if ($search_line =~ /full_name\=(.*)\s*/) {
            $search_name = $1;
        }
   
        # If there is a match, we push their details to the array     
        if ($search_line =~ /zid\=(.*)\s*/) {
            my $zid = "<font color=\'#999999\'>zID</font> $1<br>\n";
            push @search_details_arr, $zid;
        }
        if ($search_line =~ /program\=(.*)\s*/) {
            my $program = "<font color=\'#999999\'>Studies</font> $1<br>\n";
            push @search_details_arr, $program;
        }
        if ($search_line =~ /home\_suburb\=(.*)\s*/) {
            my $location = $1;
            if ($location eq "University Of New South Wales") {
                $location = "UNSW";
            }
            my $home_suburb = "<font color=\'#999999\'>From</font> $location<br>\n";
            push @search_details_arr, $home_suburb;
        }
        
        
        # If there is a match, we create the search results
        if ($search_name =~ /$search/i) {
        
            # Each search result is its own box
            my $search_box = "
      <div class=\"col-sm-6 col-md-4\">
        <div class=\"thumbnail\">
            <a href=\"?user=$search_zid\">
            <img src=\"$users_dir/$search_zid/profile.jpg\" onerror=\"this.src=\'images/default.gif\'\" />
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
    
    # Returns the page of all the search results
    return <<eof
    $search_heading
    @search_results_list
    </div> 
eof
}

#
# HTML placed at the top of every page
#
sub page_header {
    my $content_header = "Content-Type: text/html";
    
    # Storing cookies already adds in the above string, so we delete it
    if ($remove_content_header) {
        $content_header = "";
    } 
    return <<eof
$content_header

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
    <!-- Below referenced from: http://stackoverflow.com/questions/16308779/how-can-i-hide-show-a-div-when-a-button-is-clicked -->
    <script type="text/javascript">
      function showhide(id) {
        var e = document.getElementById(id);
        e.style.display = (e.style.display == 'block') ? 'none' : 'block';
      }
    </script>
  </head>
  
eof
}


#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    # Footer is just a small segment for copyright
    # Referenced from: https://blackrockdigital.github.io/startbootstrap-landing-page/
    return <<eof
    <!-- Footer -->
    <br><br>
    <footer>
        <div class=\"container\">
            <div class=\"row\">
                <div class=\"col-lg-12\">
                    <ul class=\"list-inline\">
                        <li>
                            <a href=\"?home=1\">Home</a>
                        </li>
                        <li class=\"footer-menu-divider\">&sdot;</li>
                        <li>
                            <a href=\"?about\">About</a>
                        </li>
                        <li class=\"footer-menu-divider\">&sdot;</li>
                        <li>
                            <a href=\"?contact\">Contact</a>
                        </li>
                    </ul>
                    <p class=\"copyright text-muted small\">Copyright &copy; z5017458 2016. All Rights Reserved</p>
                </div>
            </div>
        </div>
    </footer>


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
