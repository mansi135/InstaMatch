from faker import Faker 
import random
from datetime import datetime
from barnum import gen_data
import zipcode

fake = Faker()

level = ['Phd', 'Masters', 'Bachelors']
fields = ['Maths', 'Science', 'Computer Engineering', 'Electronics', 'Information Tech', 'Arts', 'Music', 'Dance']
drink_smoke = ['Yes', 'No', 'Occasionally', 'rarely']
current_relationship = ['Never Married', 'Divorced', 'Its complicated', 'Broken Hearted']
want_kids_options = ['Yes', 'No', 'Not too soon', 'May be later']

# added state, seed interests also, dr, sm, rel, ki
# w overwrites, a appends
# with open('seed_data/user.txt', 'w') as f:
#     for i in range(1,501):
#         uid = i
#         email = fake.email()
#         password = fake.password()
#         p = fake.profile()
#         fname = p['name'].split(" ")[0]
#         lname = fake.last_name()

#         aboutme = " ".join([fake.catch_phrase() for i in range(10)])
#         gender = p['sex']
#         year = random.choice(range(1970, 2002))
#         month = random.choice(range(1, 13))
#         day = random.choice(range(1, 29))
#         dob = str(datetime(year, month, day)).split(" ")[0]
#         height = random.randint(120, 200)
#         ethnicity = random.randint(1, 8)
#         religion = random.randint(1, 8)
#         drink = random.choice(drink_smoke)
#         smoke = random.choice(drink_smoke)
#         relation_status = random.choice(current_relationship)
#         want_kids = random.choice(want_kids_options)

#         address = p['address'].split("\n")[0]
#         #city = fake.city()

#         # instead of using entire US, for demostration just use CA zipcodes 90001-96162, oregon - 97001 -97920, 
#         while True:
#             zipc = fake.zipcode()
#             myzip = zipcode.isequal(str(zipc))
#             if myzip and myzip.state == 'CA':
#                 break

#         # zipc = random.choice(range(90001, 96163))
#         city = myzip.city
#         state = myzip.state
#         phone = fake.phone_number()


#         emp = p['company']
#         occ = p['job']
#         edu = random.choice(level) + " in " + random.choice(fields)

#         print >> f, str(uid) + "|" + email + "|" + password + "|" + fname + "|" + lname \
#                              + "|" + dob + "|" + str(height) + "|" + gender + "|" + str(ethnicity) + "|" + str(religion) \
#                              + "|" + drink + "|" + smoke + "|" + relation_status + "|" + want_kids \
#                              + "|" + address + "|" + city + "|" + state + "|" + zipc + "|" + phone \
#                              + "|" + emp + "|" + occ + "|" + edu + "|" + aboutme


with open('seed_data/user_interest.txt', 'w') as f:
    for i in range(1,201):
        u_interest_id = i
        random_uid = random.randint(1, 501)
        random_interestid = random.randint(1, 21)

        print >> f, str(u_interest_id) + "|" + str(random_uid) + "|" + str(random_interestid)
