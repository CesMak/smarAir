#!/usr/bin/python3

# TODO:
# once  a week make a pickle format of all txt files and kick out many data points!
# make this as extra service and read pickle files in here as well!

import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

# required for plotting and file handling
import operator
import os
import fileinput
import re
from time import strptime
import matplotlib.pyplot as plt
import matplotlib.dates
import datetime

password_send_mail = ''          # TODO edit PW here!
email_add          = '2f4yor@gmail.com'     # check if sending works: https://myaccount.google.com/lesssecureapps?pli=1
send_mail_to       = 'lamprechtmarkus1@gmail.com'

#for local tests: /home/markus/Documents/PIZero/data/twoDHTSensor
#on the pi: /home/pi
logging_files_dir  = "/home/pitwo/temp"
include_min_max    = True # include min, max points in the plots

def send_mail(send_from, send_to, subject, message, files=[],
              server="smtp.gmail.com", port=587, username=email_add, password=password_send_mail,
              use_tls=True):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

def get_logging_files(home_dir=logging_files_dir, ends_with="_logging.txt"):
    log_files = []
    for file in os.listdir(home_dir):
        if file.endswith(ends_with):
            log_files.append(os.path.join(home_dir, file))
    return log_files

def merge_log_files(files):
    # make log files nice and merge them!
    lines_without_header = []
    sorted_lines = []
    lines = list(fileinput.input(files))
    with fileinput.input(files=(files)) as f:
        for line in f:
             if not( "DateTime" in line) and "\t" in line:
                 line = line.replace("\n","")
                 lines_without_header.append(line)
    #DateTime	Entry	Power	Temperature_outside	Humidity_outside	Temperature_inside	Humidity_inside
    # one entry=2022-02-14 07:51:02 \t2975\t19.8\t54.3'
    t_fmt = '%Y-%m-%d %H:%M:%S ' # format of time stamps
    t_pat = re.compile("(^.*?)(\t)") # pattern to extract timestamp
    result = {}
    result["dates"]       = []
    result["humidity_outside"]    = []
    result["humidity_inside"]     = []
    result["temperature_outside"] = []
    result["temperature_inside"]  = []
    #usefull for debugging:
    # for i in lines_without_header:
    #     print(i)
    #     print(strptime(t_pat.search(i).group(1), t_fmt))
    for l in sorted(lines_without_header, key=lambda l: strptime(t_pat.search(l).group(1), t_fmt)):
        p = l.split("\t")
        result["dates"].append(p[0])
        result["humidity_outside"].append(float(p[3]))
        result["temperature_outside"].append(float(p[2]))
        if len(p)>4:
            result["humidity_inside"].append(float(p[5]))
            result["temperature_inside"].append(float(p[4]))
    return result

def annot_max_min(x,y, ax=None):
    xmax = x[y.index(max(y))]
    ymax = max(y)
    xmin = x[y.index(min(y))]
    ymin = min(y)
    if ymax<100 and ymin>-100:
        textmax= "y={:.1f}".format(ymax)+"\nx="+str(xmax)
        textmin= "y={:.1f}".format(ymin)+"\nx="+str(xmin)
        if not ax:
            ax=plt.gca()
        bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.7)
        arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
        kw = dict(xycoords='data', textcoords="offset points",
                  arrowprops=arrowprops, bbox=bbox_props)
        ax.annotate(textmax, xy=(xmax, ymax), xytext=(10, 10), fontsize=6, **kw)
        ax.annotate(textmin, xy=(xmin, ymin), xytext=(10, 10), fontsize=6, **kw)

def plot_file(x, y1, y2, last_values=0):
    # delete empty lists:
    y1 = [t for t in y1 if t != []]
    y2 = [t for t in y2 if t != []]
    yy1 = []
    yy2 = []
    limit_temp = False  # cause of invalid values = -111, -222
    limit_hum  = False # cause of invalid values
    name = "last_"+str(len(x))+".png"
    if len(x)<last_values:
        print("not enogh data points! - do not plot for", last_values)
        return logging_files_dir+"/"+name

    if last_values == 0: # plot all
        yy1 = y1
        yy2 = y2
    else:
        for i in y1:
            yy1.append(i[-last_values:])
        for i in y2:
            yy2.append(i[-last_values:])
        x = x[-last_values:]
    name = "last_"+str(len(x))+".png"
    try:
        fig, axs = plt.subplots(2)
        fig.suptitle('Temperature and Humidity')
        colors_hum = ['*r','*m','*y']
        labels     = ['out','in']
        colors_temp=['*b','*c','*b']
        for c,i in enumerate(yy1):
            axs[0].plot(x, i, colors_hum[c], label="tmp_"+labels[c])
            if include_min_max:
                annot_max_min(x, i, axs[0])
            if abs(max(i, key=abs))>100:
                limit_temp = True
        for c,j in enumerate(yy2):
            axs[1].plot(x, j, colors_temp[c], label="hum_"+labels[c])
            if include_min_max:
                annot_max_min(x, j, axs[1])
            if abs(max(j, key=abs))>100:
                limit_hum = True
        if limit_temp:
            axs[0].set_ylim([-30, 50]) # temperature
        if limit_hum:
            axs[1].set_ylim([0, 100]) # hum
        axs[0].legend()
        axs[1].legend()
        plt.gcf().autofmt_xdate()
        plt.savefig(logging_files_dir+"/"+name)
    except Exception as e:
        print("it did not work to plot "+name+e)
        return ""

    return logging_files_dir+"/"+name

def plot_files():
    # get all logging files with name _logging.txt in /home/file
    log_files = get_logging_files(home_dir=logging_files_dir)
    if len(log_files)==0:
        print("No logging files found!")
        print("Cannot generate an image")
        return []
    else:
        print("I found "+str(len(log_files))+" logging files.")
    result = merge_log_files(log_files)
    # one sorted line looks like: 2022-02-21 16:39:52 	31107	19.9	56.4
    if not len(result["dates"])>10:
        print("Sry nothing is plotted your logging just contains: "+str(len(log_files))+" lines.")
        return []

    # plot the images here:
    x = [datetime.datetime.strptime(d,"%Y-%m-%d %H:%M:%S ") for d in result["dates"]]
    y1=[result["temperature_outside"]]
    y2=[result["humidity_outside"]]
    if len(result)>3:
        y1 = [result["temperature_outside"], result["temperature_inside"]]
        y2 = [result["humidity_outside"], result["humidity_inside"]]
    result_files = []
    result_files.append(plot_file(x,y1,y2, last_values=100))
    result_files.append(plot_file(x,y1,y2, last_values=1000))
    result_files.append(plot_file(x,y1,y2, last_values=5000))
    result_files.append(plot_file(x,y1,y2, last_values=10000))
    result_files.append(plot_file(x,y1,y2, last_values=500000))
    result_files.append(plot_file(x,y1,y2, last_values=0))
    return result_files

img_file_names = plot_files()
send_mail(email_add, send_mail_to, "Temperature and Humidity values", "", files=img_file_names)
