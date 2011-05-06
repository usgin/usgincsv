from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
import datetime, os, csv, time, djangotasks

ROOT_DATA_LOCATION = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
DATA_STORE = FileSystemStorage(location=ROOT_DATA_LOCATION, base_url='/csv-uploads/')

def data_location(instance, filename):
    gen_user = instance.return_email.split('@')[0]
    return os.path.join(gen_user, filename)

class CsvUpload(models.Model):
    name = models.CharField(max_length=50)
    csv_file = models.FileField(upload_to=data_location,
                                storage=DATA_STORE,
                                help_text='Allowed extensions: .csv')
    return_email = models.EmailField()
    upload_time = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.name + ' -- Reply to: ' + str(self.return_email)

    def clean(self):
        # Set the Upload Time
        self.upload_time = datetime.datetime.now()
        
        # Make sure that the uploaded file is valid CSV
        try:
            csv.DictReader(self.csv_file)
        except:
            raise ValidationError('Uploaded file is not a valid CSV file.')
        
    def run_conversion(self):
        folder_path = '/Users/ryan/Documents/git/usgincsv/data/tasks'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        f = open(os.path.join(folder_path, 'finished.txt'), 'w')
        f.write('Ran the task.')
        f.close()
        
djangotasks.register_task(CsvUpload.run_conversion, "Convert CSV File to XML Metadata.")