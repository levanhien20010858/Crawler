from fastapi import FastAPI
from fastapi.responses import FileResponse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import time
from datetime import datetime
from bs4 import BeautifulSoup
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()
job_data = []
def detached_date(day):
    # Tách lấy ngày, tháng và năm từ chuỗi
    parts = day.split()
    month = parts[2]
    day = parts[3][:-1]
    year = parts[4][:-1]  # Loại bỏ dấu '.'

    # Tạo một từ điển để ánh xạ tên tháng về số tháng
    month_mapping = {
        'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
        'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
    }

    # Lấy số tháng từ từ điển ánh xạ
    month = month_mapping[month]

    # Định dạng lại ngày thành "dd/mm/yyyy"
    formatted_date = f"{day}/{month:02d}/{year}"
    return formatted_date

@app.get("/getdata")
async def root():
    driver = webdriver.Chrome()
    url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    driver.get(url)
    sleep(2)

    log = open('login.txt')
    line = log.readlines()
    username = line[2]
    password = line[1]

    print('-----Finish import the login-----')
    email_field = driver.find_element(By.ID,"username")
    email_field.send_keys(username)
    print('-----Finish keying in email-----')
    sleep(2)
    password_field = driver.find_element(By.NAME,'session_password')
    password_field.send_keys(password)
    print('-----Finish keying in password-----')
    sleep(2)
    # try:
    #   login_field = driver.find_element(By.CLASS_NAME,'btn__primary--large from__button--floating')
    #   login_field.click()
    # except NotImplementedError:
    #   print('-----Toang-----')
    # print('-----Finish logging in-----')
    name_csv = 'database1.csv'
    with open(name_csv,'w',newline='',encoding='utf-8-sig') as file_output:
        headers = ['image','title','company', 'companyurl','location','posttime','formwork','worktime','skill','aboutthejob','urlPage']
        writer = csv.DictWriter(file_output,delimiter=',',lineterminator='\n',fieldnames=headers)
        writer.writeheader()
        for i in range (100):
            print(i)
            url_ = 'https://www.linkedin.com/jobs/search/?currentJobId=3729558956&keywords=vietnam&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION&start='
            url = f"{url_}{i*25}"
            driver.get(url)
            sleep(3)
            target_div = driver.find_element(By.XPATH,'//*[@id="main"]/div/div[1]/div')
            num_scrolls = 7  # Số lần cuộn
            scroll_distance = 544  # Khoảng cách mỗi lần cuộn (pixels)
            sleep(5)
            # Cuộn từ từ
            for _ in range(num_scrolls):
                driver.execute_script("arguments[0].scrollTop += arguments[1];", target_div, scroll_distance)
                time.sleep(1)  # Tạm dừng 1 giây giữa các lần cuộn

            page_source = BeautifulSoup(driver.page_source)
            #Tìm link Job
            Jobs = page_source.find_all('a',class_ ='disabled ember-view job-card-container__link job-card-list__title')
            all_Jobs_URL = []
            for job in Jobs:
                job_ID = job.get('href')
                job_URL = "https://www.linkedin.com" + job_ID
                if job_URL not in all_Jobs_URL:
                    all_Jobs_URL.append(job_URL)
            print(len(all_Jobs_URL))
            # Tìm địa chỉ
            Locations = page_source.find_all('div',class_ ='flex-grow-1 artdeco-entity-lockup__content ember-view')
            all_Location = []

            for location in range (len(Locations)):
                ul_tag = Locations[location].find_all('ul', class_='job-card-container__metadata-wrapper')
                li_tags = ul_tag[0].find_all('li')
                str_location = li_tags[0].get_text(strip=True)
                all_Location.append(str_location)
            
            #Tìm tên company
            all_company = []
            company_div = page_source.find_all('div', class_='artdeco-entity-lockup__subtitle ember-view')
            for x in range (len(company_div)):
                company_ = company_div[x].find('span')
                company = company_.get_text(strip=True)
                all_company.append(company)

            # Truy cập từng link
            for linkedin_URL in range (len(all_Jobs_URL)):
                driver.get(all_Jobs_URL[linkedin_URL])
                # Đợi cho đến khi trang được tải xong 
                try:
                    wait = WebDriverWait(driver, 10)  # Đợi tối đa 10 giây
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pt5')))  # Đợi cho đến khi phần tử có class 'p5' xuất hiện trên trang
                except Exception:
                    print('-')
                page_source = BeautifulSoup(driver.page_source,"html.parser")
                sleep(2)
                # link logo
                job_information = page_source.find('div',class_  = "p5")
                job_image = job_information.find('div',class_ = "ivm-view-attr__img-wrapper display-flex")
                job_image_link = job_image.find_all('img')
                link = job_image_link[0].get('src') if len(job_image_link) != 0 else ''
                # print("link ảnh: " + link)
                
                # nội dung
                job_title = job_information.find('h1',class_ = "t-24 t-bold job-details-jobs-unified-top-card__job-title").get_text().strip()
                # print("Tiêu đề: " + job_title)
                
                #Địa điểm
                job_timeAndcty = ''
                try:
                    job_location = all_Location[linkedin_URL]
                    job_timeAndcty = job_information.find('div',class_ = "job-details-jobs-unified-top-card__primary-description")
                except Exception:
                    job_timeAndcty = ''
                    
                # print("Địa điểm: " + job_location)
                
                #Công ty
                job_link_company = ''
                try:
                    job_link_company_ = job_timeAndcty.find_all('a')
                    job_link_company = job_link_company_[0].get('href')
                except Exception:
                    job_link_company = ''
                
                # print("URl công ty: " + job_link_company)
                job_cty_  = all_company[linkedin_URL]
                # print("Tên công ty: " + job_cty_)
                # Thời gian đăng
                job_time_p = page_source.find('p',class_ ='t-black--light t-14 mt4')
                job_time_ = job_time_p.get_text(strip=True)
                job_time = detached_date(job_time_)
                print("Thời gian đăng: " + job_time)

                
                #-------------------------------------------------------
                data_content = job_information.find('div',class_ = 'mt5 mb2')
                data_content_ = data_content.find_all('li')
                #Data của Hình thức làm việc và Thời gian làm việc
                data_formworkandworkingtime_ = data_content_[0].find('span')
                data_formworkandworkingtime = data_formworkandworkingtime_.find_all('span')
                #Hình thức làm việc 
                job_form_work = data_formworkandworkingtime[0].get_text().strip() if len(data_formworkandworkingtime) != 0 else ''
                # print("Hình thức làm việc: " + job_form_work)
                #Thời gian làm việc
                job_working_time = data_formworkandworkingtime[1].get_text().strip() if len(data_formworkandworkingtime) >= 2 else ''
                # print("Thời gian làm việc: " +job_working_time)
                # Về công việc
                about_the_job = ''
                try:
                    about_the_job_ = page_source.find('div',class_ = "jobs-box__html-content jobs-description-content__text t-14 t-normal jobs-description-content__text--stretch")
                    about_the_job = about_the_job_.find('span')
                except Exception:
                    about_the_job = ""
                #Kỹ năng
                skill_div = page_source.find('div',class_ = 'display-flex flex-column overflow-hidden')
                skill = ''
                try:
                    skill_a = skill_div.find_all('a')
                    skill = skill_a[0].get_text().strip()
                except Exception:
                    print('')
                job_link_page = all_Jobs_URL[linkedin_URL]
                
                writer.writerow({headers[0]: link,headers[1]: job_title,headers[2]: job_cty_,headers[3]: job_link_company,headers[4]: job_location,headers[5]:job_time,headers[6]:job_form_work,headers[7]:job_working_time,headers[8]:skill,headers[9]:about_the_job,headers[10]:job_link_page})
                job_data.append({
                    "link": link,
                    "job_title": job_title,
                    "job_cty_": job_cty_,
                    "job_link_company": job_link_company,
                    "job_location": job_location,
                    "job_time": job_time,
                    "job_form_work": job_form_work,
                    "job_working_time": job_working_time,
                    "skill": skill,
                    # "about_the_job": about_the_job,
                    "job_link_page": job_link_page
                })
                
    sleep(5)
    return {"message": job_data}

@app.get("/crawl")
async def crawl():
    file_path = 'D:/New folder/New folder/database.csv'
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)

        data = []
        for row in reader:
            link = row[0]
            job_title = row[1]
            job_cty_ = row[2]
            job_link_company = row[3]
            job_location = row[4]
            job_time = row[5]
            job_form_work = row[6]
            job_working_time = row[7]
            skill = row[8]
            job_link_page = row[10]
            data.append({
                        "link": link,
                        "job_title": job_title,
                        "job_cty_": job_cty_,
                        "job_link_company": job_link_company,
                        "job_location": job_location,
                        "job_time": job_time,
                        "job_form_work": job_form_work,
                        "job_working_time": job_working_time,
                        "skill": skill,
                        # "about_the_job": about_the_job,
                        "job_link_page": job_link_page
                    })
    return {"message": data}

@app.get("/datanew")
async def crawl():
    file_path = 'D:/New folder/New folder/database2.csv'
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        next(reader, None)

        data = []
        for row in reader:
            link = row[0]
            job_title = row[1]
            job_cty_ = row[2]
            job_link_company = row[3]
            job_location = row[4]
            job_time = row[5]
            job_form_work = row[6]
            job_working_time = row[7]
            skill = row[8]
            job_link_page = row[10]
            data.append({
                        "link": link,
                        "job_title": job_title,
                        "job_cty_": job_cty_,
                        "job_link_company": job_link_company,
                        "job_location": job_location,
                        "job_time": job_time,
                        "job_form_work": job_form_work,
                        "job_working_time": job_working_time,
                        "skill": skill,
                        # "about_the_job": about_the_job,
                        "job_link_page": job_link_page
                    })
    return {"message": data}
# Trả về các tin mới trong csv mới
def findjob(driver):
    # driver = webdriver.Chrome()
    url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    driver.get(url)
    sleep(2)

    log = open('login.txt')
    line = log.readlines()
    username = line[2]
    password = line[1]

    print('-----Finish import the login-----')
    email_field = driver.find_element(By.ID,"username")
    email_field.send_keys(username)
    print('-----Finish keying in email-----')
    sleep(2)
    password_field = driver.find_element(By.NAME,'session_password')
    password_field.send_keys(password)
    print('-----Finish keying in password-----')
    sleep(2)

    for i in range(40):
        file_path = 'D:/New folder/New folder/database.csv'
        linkpage = ''
        startline = 2
        desired_row = startline + i
        x = 0
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
            reader = csv.reader(file)

            for row_number, row in enumerate(reader, 1):
                if row_number == desired_row:
                    linkpage = row[10]  # Lấy giá trị cột thứ hai
                    break

        page_source = BeautifulSoup(driver.page_source)
        driver.get(linkpage)
        a = page_source.find('div', class_ = 'jobs-details-top-card__apply-error t-12 t-bold artdeco-inline-feedback artdeco-inline-feedback--error ember-view')
        # Nếu không thấy "No longer accepting applications" trong trang 
        all_jobs_url = []
        all_location = []
        all_company = []
        all_job = []
        if a == None:
            for j in range (40):
                url_ = 'https://www.linkedin.com/jobs/search/?currentJobId=3729558956&keywords=vietnam&origin=BLENDED_SEARCH_RESULT_CARD_NAVIGATION&start='
                url = f"{url_}{j*25}"
                driver.get(url)
                sleep(3)
                target_div = driver.find_element(By.XPATH,'//*[@id="main"]/div/div[1]/div')
                num_scrolls = 7  # Số lần cuộn
                scroll_distance = 544  # Khoảng cách mỗi lần cuộn (pixels)
                sleep(5)
                # Cuộn từ từ
                for _ in range(num_scrolls):
                    driver.execute_script("arguments[0].scrollTop += arguments[1];", target_div, scroll_distance)
                    time.sleep(1)  # Tạm dừng 1 giây giữa các lần cuộn

                page_source = BeautifulSoup(driver.page_source)
                #Tìm link Job
                jobs = page_source.find_all('a',class_ ='disabled ember-view job-card-container__link job-card-list__title')
                locations = page_source.find_all('div',class_ ='flex-grow-1 artdeco-entity-lockup__content ember-view')
                company_div = page_source.find_all('div', class_='artdeco-entity-lockup__subtitle ember-view')
                
                for job in  range (len(jobs)):
                    job_id = jobs[job].get('href')
                    job_url = "https://www.linkedin.com" + job_id
                    path1 = linkpage.split("/")[5]
                    path2 = job_url.split("/")[5]
                    
                    ul_tag = locations[job].find_all('ul', class_='job-card-container__metadata-wrapper')
                    li_tags = ul_tag[0].find_all('li')
                    str_location = li_tags[0].get_text(strip=True)
                    
                    company_ = company_div[job].find('span')
                    company = company_.get_text(strip=True)
                    
                    if job_url not in all_jobs_url:
                        if path1 == path2:
                            return all_job
                        all_jobs_url.append(job_url)
                        all_location.append(str_location)
                        all_company.append(company)
                        all_job.append([all_jobs_url[job],all_location[job],all_company[job]])
                
                
            # print(len(all_job))
            return all_job
@app.get("/updatedata")
async def update():
    driver = webdriver.Chrome()
    addjob = findjob(driver)
    print('so luong: ',len(addjob))
    file_path = 'D:/New folder/New folder/database.csv'
    with open(file_path, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        data_ = list(reader)
        data = []

        for linkedin_URL in range (len(addjob)):
            
            driver.get(addjob[linkedin_URL][0])
            # Đợi cho đến khi trang được tải xong 
            try:
                wait = WebDriverWait(driver, 10)  # Đợi tối đa 10 giây
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pt5')))  # Đợi cho đến khi phần tử có class 'p5' xuất hiện trên trang
            except Exception:
                print('-')
            page_source = BeautifulSoup(driver.page_source,"html.parser")
            sleep(2)
            # link logo
            job_information = page_source.find('div',class_  = "p5")
            job_image = job_information.find('div',class_ = "ivm-view-attr__img-wrapper display-flex")
            job_image_link = job_image.find_all('img')
            link = job_image_link[0].get('src') if len(job_image_link) != 0 else ''
            # print("link ảnh: " + link)
            
            # nội dung
            job_title = job_information.find('h1',class_ = "t-24 t-bold job-details-jobs-unified-top-card__job-title").get_text().strip()
            # print("Tiêu đề: " + job_title)
            
            #Địa điểm
            job_timeAndcty = ''
            try:
                job_location = addjob[linkedin_URL][1]
                job_timeAndcty = job_information.find('div',class_ = "job-details-jobs-unified-top-card__primary-description")
            except Exception:
                job_timeAndcty = ''
                
            # print("Địa điểm: " + job_location)
            
            #Công ty
            job_link_company = ''
            try:
                job_link_company_ = job_timeAndcty.find_all('a')
                job_link_company = job_link_company_[0].get('href')
            except Exception:
                job_link_company = ''
            
            # print("URl công ty: " + job_link_company)
            job_cty_  = addjob[linkedin_URL][2]
            # print("Tên công ty: " + job_cty_)
            # Thời gian đăng
            job_time_p = page_source.find('p',class_ ='t-black--light t-14 mt4')
            job_time_ = job_time_p.get_text(strip=True)
            job_time = detached_date(job_time_)
            # print("Thời gian đăng: " + job_time)

            
            #-------------------------------------------------------
            data_content = job_information.find('div',class_ = 'mt5 mb2')
            data_content_ = data_content.find_all('li')
            #Data của Hình thức làm việc và Thời gian làm việc
            data_formworkandworkingtime_ = data_content_[0].find('span')
            data_formworkandworkingtime = data_formworkandworkingtime_.find_all('span')
            #Hình thức làm việc 
            job_form_work = data_formworkandworkingtime[0].get_text().strip() if len(data_formworkandworkingtime) != 0 else ''
            # print("Hình thức làm việc: " + job_form_work)
            #Thời gian làm việc
            job_working_time = data_formworkandworkingtime[1].get_text().strip() if len(data_formworkandworkingtime) >= 2 else ''
            # print("Thời gian làm việc: " +job_working_time)
            # Về công việc
            about_the_job = ''
            try:
                about_the_job_ = page_source.find('div',class_ = "jobs-box__html-content jobs-description-content__text t-14 t-normal jobs-description-content__text--stretch")
                about_the_job = about_the_job_.find('span')
            except Exception:
                about_the_job = ""
            #Kỹ năng
            skill_div = page_source.find('div',class_ = 'display-flex flex-column overflow-hidden')
            skill = ''
            try:
                skill_a = skill_div.find_all('a')
                skill = skill_a[0].get_text().strip()
            except Exception:
                print('')
            job_link_page = addjob[linkedin_URL][0]
            
            # Dòng mới bạn muốn thêm vào
            new_row = [link,job_title,job_cty_,job_link_company,job_location,job_time,job_form_work,job_working_time,skill,about_the_job,job_link_page]


            # Thêm dòng mới vào danh sách dữ liệu
            
            data.insert(linkedin_URL + 1, new_row)
            data_.insert(linkedin_URL + 1, new_row)
    file_path1 = 'D:/New folder/New folder/database2.csv'
    file_path2 = 'D:/New folder/New folder/database3.csv'
    with open(file_path1, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    with open(file_path2, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data_)
    

