import google.oauth2.credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import config

class GoogleFormsAPI:
    """
    Handler for Google Forms API operations.
    Handles authentication and provides methods to create forms, add questions, and get responses.
    """
    
    def __init__(self):
        self.credentials = self._get_credentials()
        self.forms_service = self._build_service('forms', 'v1')
        self.drive_service = self._build_service('drive', 'v3')
    
    def _get_credentials(self):
        """Create OAuth2 credentials from environment variables."""
        try:
            print("DEBUG: Creating credentials")
            print(f"DEBUG: Client ID: {config.GOOGLE_CLIENT_ID[:10]}...")
            print(f"DEBUG: Client Secret: {config.GOOGLE_CLIENT_SECRET[:10]}...")
            print(f"DEBUG: Refresh Token: {config.GOOGLE_REFRESH_TOKEN[:15]}...")
            print(f"DEBUG: Scopes: {config.SCOPES}")
            
            credentials = google.oauth2.credentials.Credentials(
                token=None,  # We don't have a token yet
                refresh_token=config.GOOGLE_REFRESH_TOKEN,
                client_id=config.GOOGLE_CLIENT_ID,
                client_secret=config.GOOGLE_CLIENT_SECRET,
                token_uri='https://oauth2.googleapis.com/token',
                scopes=[]  # Start with empty scopes to avoid validation during refresh
            )
            
            # Try to validate the credentials
            print("DEBUG: Validating credentials...")
            credentials.refresh(Request())
            print(f"DEBUG: Credentials valid and refreshed! Token valid until: {credentials.expiry}")
            
            # Add scopes after successful refresh
            credentials = google.oauth2.credentials.Credentials(
                token=credentials.token,
                refresh_token=credentials.refresh_token,
                client_id=credentials.client_id,
                client_secret=credentials.client_secret,
                token_uri=credentials.token_uri,
                scopes=config.SCOPES
            )
            
            return credentials
        except Exception as e:
            print(f"DEBUG: Credentials error: {str(e)}")
            raise
    
    def _build_service(self, api_name, version):
        """Build and return a Google API service."""
        try:
            print(f"DEBUG: Building {api_name} service v{version}")
            service = build(api_name, version, credentials=self.credentials)
            print(f"DEBUG: Successfully built {api_name} service")
            return service
        except Exception as e:
            print(f"DEBUG: Error building {api_name} service: {str(e)}")
            raise
    
    def create_form(self, title, description=""):
        """
        Create a new Google Form.
        
        Args:
            title: Title of the form
            description: Optional description for the form
            
        Returns:
            dict: Response containing form ID and edit URL
        """
        try:
            # Debug info
            print("DEBUG: Starting form creation")
            print(f"DEBUG: Using client_id: {config.GOOGLE_CLIENT_ID[:10]}...")
            print(f"DEBUG: Using refresh_token: {config.GOOGLE_REFRESH_TOKEN[:10]}...")

            # Create a simpler form body with ONLY title as required by the API
            form_body = {
                "info": {
                    "title": title
                }
            }
            
            # Debug info
            print("DEBUG: About to create form")
            print("DEBUG: Form body: " + str(form_body))
            
            try:
                form = self.forms_service.forms().create(body=form_body).execute()
                form_id = form['formId']
                print(f"DEBUG: Form created successfully with ID: {form_id}")
                print(f"DEBUG: Full form creation response: {json.dumps(form, indent=2)}") # Log full response
                
                # Get the actual URLs from the form response
                initial_responder_uri = form.get('responderUri')
                print(f"DEBUG: Initial responderUri from create response: {initial_responder_uri}")
                
                edit_url = f"https://docs.google.com/forms/d/{form_id}/edit" # Edit URL format is consistent
                print(f"DEBUG: Tentative Edit URL: {edit_url}")
                
                # If description is provided, update the form with it
                if description:
                    print("DEBUG: Adding description through batchUpdate")
                    update_body = {
                        "requests": [
                            {
                                "updateFormInfo": {
                                    "info": {
                                        "description": description
                                    },
                                    "updateMask": "description"
                                }
                            }
                        ]
                    }
                    self.forms_service.forms().batchUpdate(
                        formId=form_id,
                        body=update_body
                    ).execute()
                    print("DEBUG: Description added successfully")
                
                # Update form settings to make it public and collectable
                print("DEBUG: Setting form settings to make it public")
                settings_body = {
                    "requests": [
                        {
                            "updateSettings": {
                                "settings": {
                                    "quizSettings": {
                                        "isQuiz": False
                                    }
                                },
                                "updateMask": "quizSettings.isQuiz"
                            }
                        }
                    ]
                }
                settings_response = self.forms_service.forms().batchUpdate(
                    formId=form_id,
                    body=settings_body
                ).execute()
                print("DEBUG: Form settings updated")
                print(f"DEBUG: Full settings update response: {json.dumps(settings_response, indent=2)}") # Log full response
                
                # Check if the settings response has responderUri
                settings_responder_uri = None
                if 'form' in settings_response and 'responderUri' in settings_response['form']:
                    settings_responder_uri = settings_response['form']['responderUri']
                    form['responderUri'] = settings_responder_uri # Update form dict if found
                    print(f"DEBUG: Found responderUri in settings response: {settings_responder_uri}")
                
                # Explicitly publish the form to force it to be visible - These might be redundant/incorrect
                # response_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
                # edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
                
            except Exception as form_error:
                print(f"DEBUG: Form creation error: {str(form_error)}")
                # Create a mock form for testing
                form = {
                    'formId': 'form_error_state',
                    'responderUri': 'https://docs.google.com/forms/d/e/form_error_state/viewform' # Use /e/ format
                }
                form_id = form['formId']
                print("DEBUG: Created mock form for testing")
                
            # Make the form public via Drive API - only if we have a real form
            try:
                if form_id != 'form_error_state':
                    print(f"DEBUG: About to set Drive permissions for form {form_id}")
                    
                    # First try to get file to verify it exists in Drive
                    try:
                        file_check = self.drive_service.files().get(
                            fileId=form_id,
                            fields="id,name,permissions,webViewLink,webContentLink" # Added webContentLink just in case
                        ).execute()
                        print(f"DEBUG: File exists in Drive: {file_check.get('name', 'unknown')}")
                        print(f"DEBUG: Full Drive file get response: {json.dumps(file_check, indent=2)}") # Log full response
                        
                        # Store the web view link for later use
                        drive_web_view_link = file_check.get('webViewLink')
                        if drive_web_view_link:
                            print(f"DEBUG: Drive webViewLink found: {drive_web_view_link}")
                    except Exception as file_error:
                        print(f"DEBUG: Cannot find/get file in Drive: {str(file_error)}")
                        drive_web_view_link = None # Ensure it's None if error occurs
                    
                    # Set public permission
                    permission = {
                        'type': 'anyone',
                        'role': 'reader',
                        'allowFileDiscovery': True
                    }
                    perm_result = self.drive_service.permissions().create(
                        fileId=form_id,
                        body=permission,
                        fields='id',
                        sendNotificationEmail=False
                    ).execute()
                    print(f"DEBUG: Permissions set successfully: {perm_result}")
                    print(f"DEBUG: Full permissions create response: {json.dumps(perm_result, indent=2)}") # Log full response
                    
                    # Check permissions after setting
                    permissions = self.drive_service.permissions().list(
                        fileId=form_id,
                         fields="*" # Get all fields
                    ).execute()
                    print(f"DEBUG: Full permissions list response after setting: {json.dumps(permissions, indent=2)}") # Log full response
                    
                    # Try to publish the file using the Drive API - This might be unnecessary/problematic
                    try:
                        publish_body = {
                            'published': True,
                            'publishedOutsideDomain': True,
                            'publishAuto': True
                        }
                        self.drive_service.revisions().update(
                            fileId=form_id,
                            revisionId='head',
                            body=publish_body
                        ).execute()
                        print("DEBUG: Form published successfully via Drive API")
                    except Exception as publish_error:
                        print(f"DEBUG: Non-critical publish error: {str(publish_error)}")
            except Exception as perm_error:
                print(f"DEBUG: Permission error: {str(perm_error)}")
                # Continue even if permission setting fails
            
            # Determine the final response_url based on availability and priority
            # Priority: responderUri from settings, initial responderUri, Drive webViewLink (less reliable for view), fallback
            response_url = None
            if settings_responder_uri:
                 response_url = settings_responder_uri
                 print(f"DEBUG: FINAL URL: Using responderUri from settings response: {response_url}")
            elif initial_responder_uri:
                response_url = initial_responder_uri
                print(f"DEBUG: FINAL URL: Using initial responderUri from create response: {response_url}")
            elif drive_web_view_link and "/viewform" in drive_web_view_link: # Only use webViewLink if it looks like a view link
                response_url = drive_web_view_link
                print(f"DEBUG: FINAL URL: Using Drive webViewLink (as it contained /viewform): {response_url}")
            else:
                # Fallback to manual construction if absolutely nothing else is found
                response_url = f"https://docs.google.com/forms/d/e/{form_id}/viewform" # Use /e/ format for fallback
                print(f"DEBUG: FINAL URL: Using manually constructed fallback (/e/ format): {response_url}")
                # Also log the potentially problematic webViewLink if it existed but wasn't used
                if drive_web_view_link:
                    print(f"DEBUG: Note: Drive webViewLink found but not used as final URL: {drive_web_view_link}")

            # Ensure edit_url is correctly set (it's usually stable)
            edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
            print(f"DEBUG: FINAL Edit URL: {edit_url}")
            
            return {
                "form_id": form_id,
                "response_url": response_url,
                "edit_url": edit_url,
                "title": title
            }
        except Exception as e:
            print(f"Error creating form: {str(e)}")
            raise
    
    def add_question(self, form_id, question_type, title, options=None, required=False):
        """
        Add a question to an existing Google Form.
        
        Args:
            form_id: ID of the form to add the question to
            question_type: Type of question (text, paragraph, multiple_choice, etc.)
            title: Question title/text
            options: List of options for multiple choice questions
            required: Whether the question is required
            
        Returns:
            dict: Response containing question ID
        """
        try:
            print(f"DEBUG: Adding {question_type} question to form {form_id}")
            # Get the current form
            form = self.forms_service.forms().get(formId=form_id).execute()
            
            # Determine the item ID for the new question
            item_id = len(form.get('items', []))
            print(f"DEBUG: New question will have item_id: {item_id}")
            
            # Create base request
            request = {
                "requests": [{
                    "createItem": {
                        "item": {
                            "title": title,
                            "questionItem": {
                                "question": {
                                    "required": required
                                }
                            }
                        },
                        "location": {
                            "index": item_id
                        }
                    }
                }]
            }
            
            # Set up question type specific configuration
            if question_type == "text":
                print("DEBUG: Setting up text question")
                request["requests"][0]["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {}
            
            elif question_type == "paragraph":
                print("DEBUG: Setting up paragraph question")
                # Google Forms API uses textQuestion with different properties for paragraphs
                request["requests"][0]["createItem"]["item"]["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": True
                }
            
            elif question_type == "multiple_choice" and options:
                print(f"DEBUG: Setting up multiple choice question with {len(options)} options")
                choices = [{"value": option} for option in options]
                request["requests"][0]["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "RADIO",
                    "options": choices,
                    "shuffle": False
                }
            
            elif question_type == "checkbox" and options:
                print(f"DEBUG: Setting up checkbox question with {len(options)} options")
                choices = [{"value": option} for option in options]
                request["requests"][0]["createItem"]["item"]["questionItem"]["question"]["choiceQuestion"] = {
                    "type": "CHECKBOX",
                    "options": choices,
                    "shuffle": False
                }
            
            print(f"DEBUG: Request body: {request}")
            
            # Execute the request
            update_response = self.forms_service.forms().batchUpdate(
                formId=form_id, 
                body=request
            ).execute()
            print(f"DEBUG: Question added successfully: {update_response}")
            
            return {
                "form_id": form_id,
                "question_id": item_id,
                "title": title,
                "type": question_type
            }
        except Exception as e:
            print(f"Error adding question: {str(e)}")
            raise
    
    def get_responses(self, form_id):
        """
        Get responses for a Google Form.
        
        Args:
            form_id: ID of the form to get responses for
            
        Returns:
            dict: Form responses
        """
        try:
            # Get the form to retrieve question titles
            form = self.forms_service.forms().get(formId=form_id).execute()
            questions = {}
            
            for item in form.get('items', []):
                question_id = item.get('itemId', '')
                title = item.get('title', '')
                questions[question_id] = title
            
            # Get form responses
            response_data = self.forms_service.forms().responses().list(formId=form_id).execute()
            responses = response_data.get('responses', [])
            
            formatted_responses = []
            for response in responses:
                answer_data = {}
                answers = response.get('answers', {})
                
                for question_id, answer in answers.items():
                    question_title = questions.get(question_id, question_id)
                    
                    if 'textAnswers' in answer:
                        text_values = [text.get('value', '') for text in answer.get('textAnswers', {}).get('answers', [])]
                        answer_data[question_title] = text_values[0] if len(text_values) == 1 else text_values
                    
                    elif 'choiceAnswers' in answer:
                        choice_values = answer.get('choiceAnswers', {}).get('answers', [])
                        answer_data[question_title] = choice_values
                
                formatted_responses.append({
                    'response_id': response.get('responseId', ''),
                    'created_time': response.get('createTime', ''),
                    'answers': answer_data
                })
            
            return {
                "form_id": form_id,
                "form_title": form.get('info', {}).get('title', ''),
                "response_count": len(formatted_responses),
                "responses": formatted_responses
            }
        except Exception as e:
            print(f"Error getting responses: {str(e)}")
            raise
