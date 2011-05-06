from django.contrib.gis import admin
from models import CsvUpload
import djangotasks

class CsvUploadAdmin(admin.ModelAdmin):
    fields = ['name', 'csv_file', 'return_email']
    
    def save_model(self, request, obj, form, change):
        obj.save()
        task = djangotasks.task_for_object(obj.run_conversion)
        djangotasks.run_task(task)
        
admin.site.register(CsvUpload, CsvUploadAdmin)
