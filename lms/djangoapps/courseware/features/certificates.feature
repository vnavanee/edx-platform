Feature: Verified certificates
    As a student,
    In order to earn a verified certificate
    I want to sign up for a verified certificate course.

    Scenario: I can submit photos to verify my identity
        Given I am logged in
        When I select the "paid" track
        And I submit a photo of my face
        And I confirm my face photo
        And I take my ID photo
        And I confirm my ID photo
        And I confirm both photos
        Then The course is added to my cart
        And I view the payment page

    Scenario: I can pay for a verified certificate
        Given I have submitted photos to verify my identity
        When I submit "<Correctness>" payment information
        Then I see that my payment was "<Status>"
        And I receive an email confirmation
        And I see that I am registered for a verified certificate course on my dashboard

        Examples:
        | Correctness  |   Status          |
        | valid        |   successful      |
        | invalid      |   unsuccessful    |

    Scenario: I can re-take photos
        Given I have submitted my "<PhotoType>" photo(s)
        When I disconfirm  my "<PhotoType>" photo(s)
        Then I can re-take my "<PhotoType>" photo(s)

        Examples:
        | PhotoType     |
        | face          |
        | ID            |
        | both          |

    Scenario: I can return to the verify flow
        Given I have started a workflow and logged out
        When I log in
        And I say "yes" to "Return to Cart"
        Then I see the verification requirements/walkthrough page

    Scenario: I can cancel verification
        Given I have started a workflow and logged out
        When I log in
        And I say "no" to "Return to Cart"
        Then I return to the student dashboard
        And My cart is empty

    Scenario: I can audit a verified certificate course
        Given I am logged in
        When I select the "audit" track
        Then I am registered for the course
        And I return to the student dashboard
