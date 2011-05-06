from django.test import TestCase
import os, shutil, models as MODELS
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

class UploadClassTest(TestCase):
    def setUp(self):
        self.test_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test-files'))
        self.valid_test_file = os.path.join(self.test_file_path, 'valid-test.csv')
        self.invalid_test_file = os.path.join(self.test_file_path, 'invalid-test.txt')
        self.valid_email = 'testing@fake.com'
        self.gen_user = self.valid_email.split('@')[0]
    
    # Some of these tests are kinda lame. I should probably be testing POSTs to the admin interface instead
    # of testing the model methods themselves.
        
    def test_valid_cleaning(self):
        new_upload = MODELS.CsvUpload(csv_file=self.valid_test_file,
                                      return_email=self.valid_email)
        # Save method should call clean?
        try:
            new_upload.full_clean()
        except ValidationError, ex:
            self.fail('Valid inputs did not pass clean method. Exception was raised: %s' % str(ex))
        
        self.assertNotEqual(new_upload.upload_time, None, 'Upload time was not assigned properly.')
            
    def test_invalid_cleaning(self):
        new_upload = MODELS.CsvUpload(csv_file=self.invalid_test_file,
                                      return_email=self.valid_email)
        self.assertRaises(ValidationError, new_upload.full_clean())
        
    def test_valid_file_placement(self):
        new_upload = MODELS.CsvUpload(csv_file=self.valid_test_file,
                                      return_email=self.valid_email)
        new_upload.full_clean()

        file_content = ContentFile(open(new_upload.csv_file.url).read())
        new_upload.csv_file.save('valid-test.csv', file_content)

        # File ought to be in the right place now
        try:
            open(os.path.join(MODELS.ROOT_DATA_LOCATION, self.gen_user, 'valid-test.csv'))
        except:
            self.fail('File was not placed in the appropriate location after being saved.')
        
    def tearDown(self):
        test_data_path = os.path.join(MODELS.ROOT_DATA_LOCATION, self.gen_user)
        if os.path.exists(test_data_path):
            shutil.rmtree(test_data_path)
        
        