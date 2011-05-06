import csvtometadata, os, zipfile, glob, shutil
from django.core.mail import EmailMessage

def get_folder_path(csvupload):
    return os.path.dirname(csvupload.csv_file.file.name)

def output_report(report, csvupload):
    report_path = os.path.join(get_folder_path(csvupload), 'report.txt')
    f = open(report_path, 'w')
    f.write('\r\n'.join(report))
    f.close()
    
def transformcsv(csvupload):
    report = csvtometadata.transformcsv(csvupload.csv_file.file.name, get_folder_path(csvupload))
    output_report(report, csvupload)

def recursive_compress(path, archive, root):
    for thing in os.listdir(path):
        p = os.path.join(path, thing)
        if not os.path.isdir(p):
            archive.write(p, os.path.relpath(p, root))
        else:
            recursive_compress(p, archive, root)
    
def compress_result(csvupload):
    folder, name = os.path.split(get_folder_path(csvupload))
    archive_path = os.path.join(folder, name + '.zip')
    archive = zipfile.ZipFile(archive_path, 'w')
    print get_folder_path(csvupload)
    recursive_compress(get_folder_path(csvupload), archive, get_folder_path(csvupload))  
    archive.close()
    print "Finished compressing"
    return archive_path

def send_results(csvupload):
    archive_path = compress_result(csvupload)
    
    report = EmailMessage(subject='Your CSV to Metadata result',
                          body='Please find attached the result of conversion of your CSV document to XML metadata.',
                          from_email='ryan.clark@azgs.az.gov',
                          to=[csvupload.return_email],)
    report.attach_file(archive_path)
    report.send()
    
def cleanup(csvupload):
    folder, name = os.path.split(get_folder_path(csvupload))
    
    archive_path = os.path.join(folder, name + '.zip')
    if os.path.exists(archive_path): os.unlink(archive_path)
    
    for name in glob.glob(os.path.join(get_folder_path(csvupload), '*')):
        if name != csvupload.csv_file.file.name:
            if os.path.isdir(name):
                shutil.rmtree(name)
            elif os.path.isfile(name):
                os.unlink(name)