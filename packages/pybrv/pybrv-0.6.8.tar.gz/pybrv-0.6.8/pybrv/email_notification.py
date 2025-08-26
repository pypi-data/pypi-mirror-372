import requests
def email_notification(current_time_et, recipient_name, subject, env, body_part, footer=None, df=None,is_failure=False,file_name=None,url=None, err_str=None):
    if df is not None:
        body = f"""
<html>
<head>
<style>
                        * {{
                            margin: 0; 
                            padding: 0; 
                            box-sizing: border-box; 
                        }}
                        .table-container {{
                                            margin: 20px;
                                            overflow-x: auto;
                                        }}
                        table {{
                            font-family: Calibri, sans-serif; 
                            border-collapse: collapse; 
                            width: auto;
                            max-width: 100%; 
                            border: 1px solid black;
                            table-layout: auto; 
                            margin-bottom: 20px;
                        }}
                        th, td {{
                            border: 1px solid black; 
                            height: auto; 
                            vertical-align: middle; 
                            padding: 10px; 
                        }}
                        th {{
                            background-color: #292f47; 
                            color: #ffffff; 
                            font-weight: bold; 
                            text-align: center; 
                        }}
                        td {{
                            text-align: center; 
                        }}
</style>
</head>
<body>
<p>Hi Team,</p><br>
<p> The following table represents <b>{df.count()} {body_part}</b> as of <b>{current_time_et}</b>.</p>
                """
 
        # df=df.toPandas()
 
        html_table = "<br><table><thead><tr>"
        headers = df.columns
        html_table += "".join(f"<th>{header}</th>" for header in headers)
        html_table += "</tr></thead><tbody>"
        for index, row in enumerate(df.collect()):
            row_color = "transparent" if index % 2 == 0 else "#F1F1F1"
            html_table += f"<tr style='background-color: {row_color};'>"
            html_table += "".join(f"<td>{row[header]}</td>" for header in headers)
            html_table += "</tr>"
        html_table += "</tbody></table>"
        body += f"<br><div style='text-align: left;'>{html_table}</div>"
    elif is_failure:
        err_line=str(body_part).split('\n')[0] 
        err=str(err_str)[:500] if err_line.strip()=='' else err_line
        body = f"""<html>
<body>
<p>Hi Team,</p>
<p>The job has been Failed At: <strong><b>{current_time_et}</b></strong> 
                            {' for file <strong><b>' + file_name + '</b></strong>' if file_name else ''}</p>
<p><b>Error Details : </b> {err}</p>
</body>
</html>"""
 
    else:
        body = f"""<body>
<p>Hi Team,</p>
<p> {body_part}</p> """
 
    body +=f"<br><br>{footer}<br><br>" if footer else ''
 
    body += """ <p>Regards,<br>Data Team</p>
</body>
</html>
            """
 
    api_data = {
                "subject": f"{env} - Databricks - {subject} - Failed" if is_failure else f"{env} - Databricks - {subject}",
                "body": body,
                "recipient": recipient_name
                }
 
    URL = url

    HEADERS = {'Content-Type': 'application/json'}
 
    try:
        resp = requests.post(url=URL, headers=HEADERS, json=api_data)
        resp.raise_for_status()
        print(f"Email Notification sent for {subject}")
        if is_failure:
           raise Exception(f'Process has been stopped due to {body_part} failure')
    except requests.exceptions.RequestException as e:
        print("Email Not Sent: API Call Error !!", e, sep='\n')
        raise Exception(f"Email Notification failed for {subject} due to API Call Error: {e}")
    except Exception as e:
        print("Email Not Sent: Exception Occurred !!", e, sep='\n')
        raise Exception(f"Email Notification failed for {subject} due to Exception: {e}")