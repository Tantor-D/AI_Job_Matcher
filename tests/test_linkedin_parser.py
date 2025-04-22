from src.parsers.linkedin_parser import LinkedInParser


if __name__ == '__main__':
    # unittest.main()
    proxies = [
        # "http://65.108.159.129:1080",
        # "http://103.152.112.120:80",
        # "http://5.161.103.41:88",
        # "http://103.152.112.157:80",
        # "http://13.38.153.36:80",
        # "http://13.37.89.201:80",
        # "http://13.37.59.99:3128",
        # "http://13.38.176.104:3128",
        # "http://13.36.104.85:80",
        # "http://13.36.113.81:3128",
        # "http://15.236.106.236:3128",
        # "http://13.37.73.214:80",
        # "http://178.16.130.81:80",
        # "http://138.91.159.185:80"
    ]

    # 出现使用了cookie后，反而无法访问的情况
    # cookie = "li_at=AQEFAHUBAAAAABIkVDsAAAGTz00wfgAAAZPzWbR-TgAAGHVybjpsaTptZW1iZXI6MTM4MjE3NTIwMT1dheYLCkyLuuOYiupxwcVDiV6_e6z_M_DlCPGkEvz4KoJ4R56gWTg4el98Flt2VCwbQtvruRfKif9-MWwjLnEOTby_kUDidj7ituF5SpAu1n5H10TqwmMSFwclKZ1pShUYNWPIJ6Z65y28oNeZEMgNxi22wj6rotXztx91D3PuPM3mZ5b0HhksJoS7c09jIHn5or4; JSESSIONID=ajax:4268297388839058447; lang=en_US;"
    cookie = None
    linkedin_parser = LinkedInParser(proxies = proxies, cookies = cookie)
    test_url = "https://www.linkedin.com/jobs/search/?currentJobId=4087409985&geoId=101008859&keywords=python%20student&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
    test_url = "https://www.linkedin.com/jobs/search/?currentJobId=4077875677&geoId=101008859&keywords=student%20software&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
    jobs = linkedin_parser.parse(test_url)
    print("len(jobs):", len(jobs))
    print(jobs)
    jobs_descriptions = linkedin_parser.format_all_job_descriptions(jobs)
    print(jobs_descriptions)
    print("finished")
