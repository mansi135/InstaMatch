from faker import Faker 
import random

fake = Faker()

religions = ['Hindu', 'Muslim', 'Sikh', 'Christian', 'Buddhist', 'Chinese tradi',
              'African tradi', 'Jews', 'Jude', 'Shinto']

ethnicities = ['South Asian', 'Asian', 'White', 'Black', 'Hispanic', 'Arabs', 'Romani',
              'Chinese', 'Pacific Islander']

# w overwrites, a appends
with open('seed_data/user.txt', 'w') as f:
    for i in range(1,101):
        uid = i
        email = fake.email()
        password = fake.password()
        fname = fake.first_name()
        lname = fake.last_name()

        dob = fake.profile()['birthdate']
        height = random.randint(150, 180)
        gender = fake.profile()['sex']
        # ethnicity = random.choice(ethnicities)
        # religion = random.choice(religions)
        ethnicity = random.randint(1, 8)
        religion = random.randint(1, 20)

        address = fake.catch_phrase()
        city = fake.city()
        zipcode = fake.zipcode()
        phone = fake.phone_number()

        emp = fake.company()
        occ = None
        edu = None
        aboutme = fake.catch_phrase()

        print >> f, str(uid) + "|" + email + "|" + password + "|" + fname + "|" + lname \
                             + "|" + dob + "|" + str(height) + "|" + gender + "|" + str(ethnicity) + "|" + str(religion) \
                             + "|" + address + "|" + city + "|" + zipcode + "|" + phone \
                             + "|" + emp + "|" + "|" + "|" + aboutme



