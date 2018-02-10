from faker import Faker 
import random
from datetime import datetime
from barnum import gen_data



fake = Faker()


# w overwrites, a appends
with open('seed_data/user.txt', 'w') as f:
    for i in range(1,501):
        uid = i
        email = fake.email()
        password = fake.password()
        p = fake.profile()
        fname = p['name'].split(" ")[0]
        lname = fake.last_name()

        #dob = fake.profile()['birthdate']
        # ethnicity = random.choice(ethnicities)
        # religion = random.choice(religions)
 
        year = random.choice(range(1950, 2003))
        month = random.choice(range(1, 13))
        day = random.choice(range(1, 29))
        dob = str(datetime(year, month, day)).split(" ")[0]

        height = random.randint(120, 200)
        gender = p['sex']

        ethnicity = random.randint(1, 8)
        religion = random.randint(1, 8)

        address = p['address'].split("\n")[0]
        city = fake.city()

        # while True:
        #     zipcode = gen_data.create_city_state_zip()[0]
        #     if len(zipcode) == 5:
        #         break
        zipcode = fake.zipcode()

        phone = fake.phone_number()

        emp = p['company']
        occ = p['job']
        edu = None
        aboutme = fake.catch_phrase()

        print >> f, str(uid) + "|" + email + "|" + password + "|" + fname + "|" + lname \
                             + "|" + dob + "|" + str(height) + "|" + gender + "|" + str(ethnicity) + "|" + str(religion) \
                             + "|" + address + "|" + city + "|" + zipcode + "|" + phone \
                             + "|" + emp + "|" + occ + "|" + "|" + aboutme



