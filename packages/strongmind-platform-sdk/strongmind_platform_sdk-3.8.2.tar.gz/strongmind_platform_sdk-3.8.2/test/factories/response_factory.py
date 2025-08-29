from faker import Faker

fake = Faker()


def response_factory(school_subdomain=None):
    subdomain = school_subdomain or fake.domain_word()
    dict_returner = lambda *args: [
        {
            "com.instructure.canvas.account": f"{subdomain}.strongmind.com:{fake.random_int(0, 9)}",
            "com.powerschool.school.dcid": f"{subdomain}.powerschool.com:{fake.random_int(10, 99)}",
            "com.powerschool.school.number": f"{subdomain}.powerschool.com:{fake.random_int(100, 200)}",
        }
    ]

    return (subdomain, dict_returner)
