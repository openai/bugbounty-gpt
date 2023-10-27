# from src.handlers.submission_handler import BugCrowdSubmission
# from src.handlers.bugcrowd_api import BugCrowdAPI
# from unittest.mock import patch

# def test_prepare_assign_data():
#     submission = BugCrowdSubmission("submission_id", None, None)
#     user_id = "user_id"
#     expected_data = {
#         'data': {
#             'type': 'submission',
#             'relationships': {
#                 'assignee': {
#                     'data': {
#                         'id': user_id,
#                         'type': 'identity'
#                     }
#                 }
#             }
#         }
#     }
#     assert submission.prepare_assign_data(user_id) == expected_data

# def test_handle_assign_response_success(caplog):
#     submission = BugCrowdSubmission("submission_id", None, None)
#     user_id = "user_id"
#     mock_response = type("Response", (object,), {"status_code": 200})
#     submission.handle_assign_response(mock_response, user_id)
#     assert f"Submission submission_id assigned to user {user_id}." in caplog.text

# def test_handle_assign_response_failure(caplog):
#     submission = BugCrowdSubmission("submission_id", None, None)
#     user_id = "user_id"
#     mock_response = type("Response", (object,), {"status_code": 400})
#     submission.handle_assign_response(mock_response, user_id)
#     assert f"Unable to assign submission submission_id to user {user_id}. Status code: 400" in caplog.text

# def test_assign_to_user():
#     submission_id = "submission_id"
#     user_id = "user_id"
#     submission = BugCrowdSubmission(submission_id, None, None)

#     with patch.object(BugCrowdAPI, 'patch_submission') as mock_patch_submission:
#         mock_response = type("Response", (object,), {"status_code": 200})
#         mock_patch_submission.return_value = mock_response

#         submission.assign_to_user(user_id)

#         # Check if the function was called with the correct parameters
#         mock_patch_submission.assert_called_once_with(submission_id, ANY) # Replace ANY with the expected data dictionary
