from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import re, time

from django.contrib.auth.models import User


### TODO break into smaller tests; helper methods?


class HomePageTest(LiveServerTestCase):
    ''' hello selenium '''

    browser = webdriver.Firefox()
    browser.get('http://localhost:8000')
    assert 'LMN' in browser.title
    browser.quit()


class BrowseArtists(LiveServerTestCase):

    fixtures = ['fn_testing_users', 'fn_testing_artists', 'fn_testing_venues', 'fn_testing_shows', 'fn_testing_notes']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)


    def tearDown(self):
        self.browser.quit()


    def test_browsing_artists(self):

        # Start on home page
        self.browser.get(self.live_server_url)

        # When searching for elements, wait 3 seconds for element to appear on page.
        # Needed because page load time is slower than this script's execution time.
        self.browser.implicitly_wait(3)

        # Find and click on artists link
        artist_list_link = self.browser.find_element_by_link_text('Artists')
        artist_list_link.click()

        artists = [ 'ACDC' , 'REM', 'Yes' ]

        artist_divs = self.browser.find_elements_by_class_name('artist')

        for artist, div in zip (artists, artist_divs):

            # assert artist name is present
            assert artist in div.text

            # find a link is present with artist name - exception raised if not found
            div.find_element_by_link_text(artist)
            # Find the link to view that artist's shows (which will lead to notes). Again, exception raised
            div.find_element_by_link_text('%s notes' % artist)


        # Are we on the right page? Do this after finding elements so know page has loaded
        assert '/artists/list/' in self.browser.current_url
        assert 'Artist List' in self.browser.page_source  # Could also put the title in a div or header element, and find that, and verify correct text.

        # Get a link to one of the artists
        rem = self.browser.find_element_by_link_text('REM')

        # click this link
        rem.click()

        # Assert that artist's info is shown on new page
        # Assert that the URL is as expected. REM pk = 1.
        artist_name = self.browser.find_element_by_id('artist_name')
        assert 'REM' in artist_name.text
        assert '/artists/detail/1' in self.browser.current_url

        # go back to artists list
        self.browser.back()

        # Get a link to that artist's shows (and to notes)
        rem_notes = self.browser.find_element_by_link_text('REM notes')
        # Click on shows/notes link
        rem_notes.click()

        title = self.browser.find_element_by_id('venues_for_artist_title')
        # On correct page? Verify title, and URL

        assert 'Venues that REM has played at' in title.text
        assert 'artists/venues_played/1' in self.browser.current_url

        # assert list of venues that artist has played at is shown, most recent first
        # Should be show pk = 2 venue 1 first ave on 2017-01-02 , show pk = 1 venue 2, turf club on 2016-11-02
        # Assert a link to add notes is shown for each show
        expected_shows =  [ { "pk" : 2 , "show_date" : "Jan. 2, 2017", "venue" : 'The Turf Club' },
        {"model" : "lmn.show", "pk" : 1 , "show_date" : "Nov. 4, 2016", "venue" : 'First Avenue' } ]

        show_divs = self.browser.find_elements_by_class_name('show')

        for show, div in zip (expected_shows, show_divs):
            assert show['venue'] in div.text
            assert show['show_date'] in div.text

        # click on one of the shows - get the first match (Turf Club, Jan 2)
        see_notes_add_own = self.browser.find_element_by_partial_link_text('See notes for this')
        see_notes_add_own.click()

        # verify list of notes for that show are shown
        # verify on correct page
        title = self.browser.find_element_by_id('show_title')
        assert 'Notes for REM at The Turf Club on Jan. 2, 2017' in title.text
        assert 'notes/for_show/2' in self.browser.current_url

        # should be two notes, awsome and ok, in that order - most recently posted first
        # Trying out a different way of finding and checking properties of elements. A loop is less typing :)

        first_note_div = self.browser.find_element_by_id('note_2')
        # Is the title (in a H3 element) 'awesome' ?
        assert 'awesome' in first_note_div.find_element_by_tag_name('h3').text
        # Check note text
        assert 'yay!' in first_note_div.text
        # By correct user?
        assert 'bob' in first_note_div.find_element_by_class_name('user').text
        # Posted on the epected day?
        assert 'Posted on Feb. 13, 2017' in first_note_div.text

        # Repeat for second note
        second_note_div = self.browser.find_element_by_id('note_1')
        assert 'ok' in second_note_div.find_element_by_tag_name('h3').text
        assert 'alright' in second_note_div.text
        assert 'alice' in second_note_div.find_element_by_class_name('user').text
        # Posted on the epected day?
        assert 'Posted on Feb. 12, 2017' in second_note_div.text

        # verify input button to add user's own notes for that show is displayed
        add_notes = self.browser.find_element_by_tag_name('input')
        self.assertEqual(add_notes.get_attribute('value'), 'Add your own notes')

        # Adding a note requires authentication - will do this in another test.


    def test_searching_artists(self):

        self.browser.get(self.live_server_url + '/artists/list')

        # Verify title
        title = self.browser.find_element_by_id('artist_list_title')
        assert 'All artists' in title.text

        # Find search form. Django gives each form input an id.

        search_input = self.browser.find_element_by_id('id_search_name')

        # ** Exact match search **

        # Enter text and submit form
        search_input.send_keys('Yes')  # one exact match
        search_input.submit()   # Convenience method to submit the form that the input belongs to.

        time.sleep(1)  # Wait for page to load. (yuck). TODO how to check for search page load?

        # Verify correct title
        title = self.browser.find_element_by_id('artist_list_title')
        assert 'Artists matching \'Yes\'' in title.text

        # Exactly one result for Yes
        assert 'Yes' in self.browser.page_source
        assert 'REM' not in self.browser.page_source
        assert 'ACDC' not in self.browser.page_source

        # ** partial text search **

        search_input = self.browser.find_element_by_id('id_search_name')

        # Enter text and submit form
        search_input.send_keys('e')  # should return two partial-text matches; search is case-insensitive
        search_input.submit()   # Convenience method to submit the form that the input belongs to.

        time.sleep(1)  # Wait for page to load. (ugh).

        # Verify correct title
        title = self.browser.find_element_by_id('artist_list_title')
        assert 'Artists matching \'e\'' in title.text

        assert 'Yes' in self.browser.page_source
        assert 'REM' in self.browser.page_source
        assert 'ACDC' not in self.browser.page_source

        # **  No matches **
        search_input = self.browser.find_element_by_id('id_search_name')

        # Enter text and submit form
        search_input.send_keys('ZZZ ZZZ')  # no exact matches
        search_input.submit()   # Convenience method to submit the form that the input belongs to.

        time.sleep(1)  # Wait for page to load. (meh).

        # Verify correct title
        title = self.browser.find_element_by_id('artist_list_title')  # id with spaces in ??
        assert 'Artists matching \'ZZZ ZZZ\'' in title.text

        assert 'Yes' not in self.browser.page_source
        assert 'REM' not in self.browser.page_source
        assert 'ACDC' not in self.browser.page_source

        # "No artists found message"

        assert 'No artists found' in self.browser.page_source

        # Find and click 'clear' button

        clear = self.browser.find_element_by_partial_link_text('clear')
        clear.click()

        time.sleep(1)  # Wait for page to load. (still yuck).

        # After search cleared, verify all artists are shown

        assert 'Yes' in self.browser.page_source
        assert 'REM' in self.browser.page_source
        assert 'ACDC' in self.browser.page_source



class BrowseVenues(LiveServerTestCase):

    fixtures = ['fn_testing_users', 'fn_testing_artists', 'fn_testing_venues', 'fn_testing_shows', 'fn_testing_notes']

    def setUp(self):
        self.browser = webdriver.Firefox()

        # When searching for elements, wait up to 3 seconds for element to appear of page. Needed
        # because page load time is slower than this script's execution time.
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()


    def test_browsing_venues(self):

        # Start on home page
        self.browser.get(self.live_server_url)

        # Find and click on venues link
        venue_list_link = self.browser.find_element_by_link_text('Venues')
        venue_list_link.click()

        venues = [ 'First Avenue' , 'Target Center', 'The Turf Club' ]

        venue_divs = self.browser.find_elements_by_class_name('venue')

        for venue, div in zip (venues, venue_divs):

            # assert venue name is present
            assert venue in div.text
            # find a link is present with venue name - exception raised if not found
            div.find_element_by_link_text(venue)
            # Find the link to view that venue's shows (which will lead to notes). Again, exception raised
            div.find_element_by_link_text('%s notes' % venue)


        # Are we on the right page? Do this after finding elements so know page has loaded
        assert '/venues/list/' in self.browser.current_url
        assert 'Venue List' in self.browser.page_source  # Could also put the title in a div or header element, and find that, and verify correct text.

        # Get a link to one of the venues
        fa = self.browser.find_element_by_link_text('First Avenue')

        # click the link to First Avenue
        fa.click()

        # Assert that venue's info is shown on new page
        # Assert that the URL is as expected. First Ave pk = 1.

        # venue_name = self.browser.find_element_by_id('venue_name')
        # assert 'First Avenue' in venue_name.text
        #

        assert 'First Avenue' in self.browser.find_element_by_id('venue_name').text
        assert 'Minneapolis' in self.browser.find_element_by_id('venue_city').text
        assert 'MN' in self.browser.find_element_by_id('venue_state').text

        assert '/venues/detail/1' in self.browser.current_url

        # go back
        self.browser.back()

        # Get a link to that venue's shows (and to notes)
        fa_notes = self.browser.find_element_by_link_text('First Avenue notes')

        # Click on shows/notes link
        fa_notes.click()

        title = self.browser.find_element_by_id('artists_at_venue_title')
        # On correct page? Verify title, and URL
        assert 'Artists that have played at First Avenue' in title.text
        assert 'venues/artists_at/1' in self.browser.current_url

        # assert list of venues that venue has played at is shown, most recent first
        # Should be show pk = 2 venue 1 first ave on 2017-01-02 , show pk = 1 venue 2, turf club on 2016-11-02
        # Assert a link to add notes is shown for each show
        expected_shows =  [ { "pk" : 4 , "show_date" : "Jan. 21, 2017", "artist" : 'ACDC' },
        { "pk" : 1 , "show_date" : "Nov. 4, 2016", "artist" : 'REM' } ]

        show_divs = self.browser.find_elements_by_class_name('show')

        for show, div in zip (expected_shows, show_divs):
            assert show['artist'] in div.text
            assert show['show_date'] in div.text

        # click on one of the shows - get the first match (ACDC, Jan 21)
        see_notes_add_own = self.browser.find_element_by_partial_link_text('See notes for this')
        see_notes_add_own.click()

        # verify list of notes for that show are shown
        # verify on correct page
        title = self.browser.find_element_by_id('show_title')
        assert 'Notes for ACDC at First Avenue on Jan. 21, 2017' in title.text
        assert 'notes/for_show/4' in self.browser.current_url

        # should be one note.

        first_note_div = self.browser.find_element_by_id('note_4')
        # Is the title (in a H3 element) 'mythical' ?
        assert 'mythical' in first_note_div.find_element_by_class_name('note_title').text
        # Check note text
        assert 'boo' in first_note_div.find_element_by_class_name('note_text').text
        # By correct user?
        assert 'cat' in first_note_div.find_element_by_class_name('user').text
        # Posted on the epected day?
        assert 'Posted on Feb. 15, 2017' in first_note_div.find_element_by_class_name('note_info').text

        # verify input button to add user's own notes for that show is displayed
        add_notes = self.browser.find_element_by_tag_name('input')
        self.assertEqual(add_notes.get_attribute('value'), 'Add your own notes')

        # Adding a note requires authentication - will do this in another test.

        # Test artist with no shows
        self.browser.back() # To list of shows
        self.browser.back() # to list of artists

        no_shows_venue = self.browser.find_element_by_link_text('Target Center notes')
        # This page should say 'we have no records of shows at this venue'
        no_shows_venue.click()

        no_show_para = self.browser.find_element_by_id('no_results')
        assert 'no records of shows' in no_show_para.text


    def test_searching_venues(self):

            self.browser.get(self.live_server_url + '/venues/list')

            # Verify title
            title = self.browser.find_element_by_id('venue_list_title')
            assert 'All venues' in title.text

            # Find search form. Django gives each form input an id.
            search_input = self.browser.find_element_by_id('id_search_name')

            # ** Exact match search **

            # Enter text and submit form
            search_input.send_keys('First Avenue')  # one exact match
            search_input.submit()   # Convenience method to submit the form that the input belongs to.

            time.sleep(1)  # Wait for page to load. (yuck). TODO better way to check for search page load? Can't search for an element to force Selenium to wait because it's the same page.

            # Verify correct title
            title = self.browser.find_element_by_id('venue_list_title')
            assert 'Venues matching \'First Avenue\'' in title.text

            # Exactly one result for First Avenue
            assert 'First Avenue' in self.browser.page_source
            assert 'Target Center' not in self.browser.page_source
            assert 'The Turf Club' not in self.browser.page_source
            # Check for no "No venues found" message
            assert 'No venues found' not in self.browser.page_source

            # ** partial text search **

            search_input = self.browser.find_element_by_id('id_search_name')

            # Enter text and submit form
            search_input.send_keys('a')  # should return two partial-text matches; search is case-insensitive
            search_input.submit()   # Convenience method to submit the form that the input belongs to.

            time.sleep(1)  # Wait for page to load. (ugh).

            # Verify correct title
            title = self.browser.find_element_by_id('venue_list_title')
            assert 'Venues matching \'a\'' in title.text

            assert 'First Avenue' in self.browser.page_source
            assert 'Target Center' in self.browser.page_source
            assert 'The Turf Club' not in self.browser.page_source
            # Check for no "No venues found" message
            assert 'No venues found' not in self.browser.page_source

            # **  No matches **
            search_input = self.browser.find_element_by_id('id_search_name')

            # Enter text and submit form
            search_input.send_keys('ZZZ ZZZ')  # no exact matches
            search_input.submit()   # Convenience method to submit the form that the input belongs to.

            time.sleep(1)  # Wait for page to load. (meh).

            # Verify correct title
            title = self.browser.find_element_by_id('venue_list_title')  # id with spaces in ??
            assert 'Venues matching \'ZZZ ZZZ\'' in title.text

            assert 'First Avenue' not in self.browser.page_source
            assert 'Target Center' not in self.browser.page_source
            assert 'The Turf Club' not in self.browser.page_source

            # Check for "No venues found" message
            assert 'No venues found' in self.browser.page_source

            # Find and click 'clear' button

            clear = self.browser.find_element_by_partial_link_text('clear')
            clear.click()

            time.sleep(1)  # Wait for page to load. (still yuck).

            # After search cleared, verify all venues are shown

            assert 'First Avenue' in self.browser.page_source
            assert 'Target Center' in self.browser.page_source
            assert 'The Turf Club' in self.browser.page_source



class TestNotes(LiveServerTestCase):

    fixtures = ['fn_testing_users', 'fn_testing_artists', 'fn_testing_venues', 'fn_testing_shows', 'fn_testing_notes']

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()


    def test_add_note_for_show_when_logged_in(self):

        self.browser.implicitly_wait(3)

        # Log in
        self.browser.get(self.live_server_url + '/accounts/login')
        username = self.browser.find_element_by_id('id_username')
        password = self.browser.find_element_by_id('id_password')
        username.send_keys('bob')
        password.send_keys('qwertyuiop')
        username.submit()

        time.sleep(1)

        # Get show page, the list of notes for an example show
        self.browser.get(self.live_server_url + '/notes/for_show/2')

        # Find and click on 'add note' button
        add_note = self.browser.find_element_by_id('add_note')
        add_note.submit()

        # Should be on add note page

        # Find form elements
        title_area = self.browser.find_element_by_id('id_title')
        text_area = self.browser.find_element_by_id('id_text')

        # Check URL (after finding elements, so will know page has loaded)
        assert 'notes/add/2' in self.browser.current_url

        title_area.send_keys('Fab')
        text_area.send_keys('Best ever')
        title_area.submit()  # Convenience method for submitting form with this element in

        # Should now be on note detail page. Title will be 'band at venue by user'

        title = self.browser.find_element_by_id('note_page_title')
        assert 'REM at The Turf Club by bob' in title.text

        note_title = self.browser.find_element_by_id('note_title')
        assert 'Fab' in note_title.text

        note_text = self.browser.find_element_by_id('note_text')
        assert 'Best ever' in note_text.text

        # Correct URL?
        assert '/notes/detail/5' in self.browser.current_url



    def test_add_note_redirect_to_login_and_back_to_add_note(self):

        # Get show page, the list of notes for an example show
        self.browser.get(self.live_server_url + '/notes/for_show/2')

        # Find and click on 'add note' button
        add_note = self.browser.find_element_by_id('add_note')
        add_note.submit()

        # Verify at login page
        username = self.browser.find_element_by_id('id_username')
        password = self.browser.find_element_by_id('id_password')
        username.send_keys('alice')
        password.send_keys('qwertyuiop')

        # Click login button
        self.browser.find_element_by_tag_name('button').submit()

        # Should be logged in and at add note form
        # Find form elements
        title_area = self.browser.find_element_by_id('id_title')
        text_area = self.browser.find_element_by_id('id_text')

        # Check URL (after finding elements, so will know page has loaded)
        assert 'notes/add/2' in self.browser.current_url

        title_area.send_keys('Fab')
        text_area.send_keys('Best ever')
        title_area.submit()  # Convenience method for submitting form with this element in

        # Should now be on note detail page. Title will be 'band at venue by user'
        title = self.browser.find_element_by_id('note_page_title')
        assert 'REM at The Turf Club by alice' in title.text

        note_title = self.browser.find_element_by_id('note_title')
        assert 'Fab' in note_title.text

        note_text = self.browser.find_element_by_id('note_text')
        assert 'Best ever' in note_text.text

        assert '/notes/detail/5' in self.browser.current_url


    def test_add_note_redirect_to_login_and_register_and_back_to_add_note(self):
        pass

        # start at list of notes

        # click add note

        # verify redirect to login

        # click register link

        # register account

        # verify redirect to add note form

        # enter note text and title

        # verify redirect to note detail (TODO you'll need to implement this feature!)


class TestRegistration(LiveServerTestCase):

    fixtures = [ 'fn_testing_users' ]

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()


    def test_login_valid_password(self):

        # Log in
        self.browser.get(self.live_server_url + '/accounts/login')
        username = self.browser.find_element_by_id('id_username')
        password = self.browser.find_element_by_id('id_password')
        username.send_keys('alice')
        password.send_keys('qwertyuiop')

        # Click login button
        self.browser.find_element_by_tag_name('button').submit()

        # Verify page contains 'you are logged in, alice'
        welcome = self.browser.find_element_by_id('welcome_user_msg')
        assert 'You are logged in, alice.' in welcome.text


    def test_login_invalid_password(self):

        # Log in
        self.browser.get(self.live_server_url + '/accounts/login')
        username = self.browser.find_element_by_id('id_username')
        password = self.browser.find_element_by_id('id_password')
        username.send_keys('none')
        password.send_keys('wrong')

        # Click login button
        self.browser.find_element_by_tag_name('button').submit()

        # Once page loads, check no welcome message (elements version, returns a list with size 0 if not found, instead of raising exception)
        welcome = self.browser.find_elements_by_id('welcome_user_msg')
        assert len(welcome) is 0

        # Verify page still says 'login or sign up'
        login_invite = self.browser.find_element_by_id('login_or_sign_up')
        assert 'Login or sign up' in login_invite.text
        # Verify page does NOT display 'you are logged in, none'
        assert 'You are logged in, none.' not in self.browser.page_source
        # Assert error message

        assert 'Please enter a correct username and password' in self.browser.page_source


    def test_register(self):
        pass
        # TODO


class TestProfilePage(LiveServerTestCase):

    fixtures = ['fn_testing_users', 'fn_testing_artists', 'fn_testing_venues', 'fn_testing_shows', 'fn_testing_notes']

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()


    def test_view_user_profile_own_notes_shown(self):

        # Get alice's (user 1) profile - one note
        self.browser.get(self.live_server_url + '/user/profile/1')
        title = self.browser.find_element_by_id('username_notes')
        assert 'alice\'s notes' in title.text

        note_divs = self.browser.find_elements_by_class_name('note')
        assert len(note_divs) is 1
        first_note = note_divs[0]
        assert 'ok' in first_note.find_element_by_class_name('note_title').text
        assert 'alright' in first_note.find_element_by_class_name('note_text').text

        assert 'REM at The Turf Club on Jan. 2, 2017' in first_note.find_element_by_class_name('note_info').text
        assert 'Feb. 12, 2017' in first_note.find_element_by_class_name('note_posted_at').text

        # Get dani's profile - no notes
        self.browser.get(self.live_server_url + '/user/profile/4')

        title = self.browser.find_element_by_id('username_notes')
        assert 'dani\'s notes' in title.text

        note_divs = self.browser.find_elements_by_class_name('note')
        assert len(note_divs) is 0
        assert 'No notes' in self.browser.find_element_by_id('no_records').text
