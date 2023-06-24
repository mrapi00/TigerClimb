import math
import re

def yds_format(grade_str):
    valid_format = re.compile('5.[1-9][0-9]*[+-]?|5.0[+-]?')
    return valid_format.match(grade_str)

def vgrade_format(grade_str):
    # unimplemented
    valid_format = re.compile('V[1-9][0-9]*[+-]?|V0[+-]?|VB')
    return valid_format.match(grade_str)

# converts arbitrary climbing grade to number
def grade_to_number(grade_str):
    # roped route grade string begins with 5
    if yds_format(grade_str):
        return yds_to_number(grade_str)
    # bouldering grade (unroped)
    elif vgrade_format(grade_str):
        return vgrade_to_number(grade_str)
    else:
        return None

# Yosemite decimal system, aka YDS, for roped routes, to number
# Examples of YDS grades: "5.11-", "5.9+", "5.8"
# returns None if invalid format
def yds_to_number(grade_str):
    if not yds_format(grade_str):
        return None
    sign = .333 # weight of "+" or "-" in grade
    grade_str = grade_str[2:]
    if grade_str[len(grade_str) - 1] == "+":
        return float(grade_str[:-1]) + sign
    elif grade_str[len(grade_str) - 1] == "-":
        return float(grade_str[:-1]) - sign
    else:
        return float(grade_str)

# V-scale bouldering grade to number
# Examples of V-grades: "V5", "V0", "V3"
def vgrade_to_number(grade_str):
    return float(grade_str[1:])

# return grade given grade_num, the real number grade, and type, either "boulder" or "roped"
def number_to_grade(grade_num, type_str):
    if (type_str == "boulder"):
        return "V" + str(grade_num)
    elif (type_str == "roped"):
        if grade_num - math.floor(grade_num) > .5:
            return "5." + str(math.ceil(grade_num)) + "-"
        elif grade_num - math.floor(grade_num) > 0:
            return "5." + str(math.floor(grade_num)) + "+"
        else:
            return "5." + str(math.floor(grade_num))

# testing the functions above
def main():
    print("V5 is", grade_to_number("V5"))
    print("V2 is", grade_to_number("V2"))
    print("5.7 is", grade_to_number("5.7"))
    print("5.7+ is", grade_to_number("5.7+"))
    print("5.10- is", grade_to_number("5.10-"))

    print("6.2 is", grade_to_number("6.2"))
    try:
        print("5.11 as a float is", grade_to_number(5.11))
    except:
        print("can't use this function on floats!")

    print("9.667 is " + number_to_grade(9.667, "roped"))
    print("10.333 is " + number_to_grade(10.333, "roped"))
    print("10 is " + number_to_grade(10, "roped"))
    print("0 is " + number_to_grade(0, "roped"))
    print("3 is " + number_to_grade(3, "boulder"))

    print("100 is", number_to_grade(100, "roped"))
    print("-1 as an int is", number_to_grade(-1, "boulder"))

    grade_base = "5."
    test_num = 100
    print()
    print("Thorough testing of number_to_grade:")
    print("Testing solid grades...")
    for i in range(test_num):
        actual_grade = grade_base + str(i)
        converted_grade = number_to_grade(i, 'roped')
        if actual_grade != converted_grade:
            print("Erroneous conversion: " + str(i) + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all solid grades")
    print("Testing plus grades...")
    for i in range(test_num):
        grade_num = i+.333
        actual_grade = grade_base + str(i) + "+"
        converted_grade = number_to_grade(grade_num, 'roped')
        if actual_grade != converted_grade:
            print("Erroneous conversion: " + grade_num + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all plus grades")
    print("Testing minus grades...")
    for i in range(test_num):
        grade_num = i-.333
        actual_grade = grade_base + str(i) + "-"
        converted_grade = number_to_grade(grade_num, 'roped')
        if actual_grade != converted_grade:
            print("Erroneous conversion: " + grade_num + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all minus grades")
    
    print()
    print("Thorough testing of grade_to_number:")
    print("Testing solid grades")
    for i in range(test_num):
        grade_str = grade_base + str(i)
        converted_grade = grade_to_number(grade_str)
        if converted_grade!=i:
            print("Erroneous conversion: " + grade_str + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all solid grades")
    print("Testing plus grades")
    for i in range(test_num):
        grade_str = grade_base + str(i) + '+'
        converted_grade = grade_to_number(grade_str)
        grade_num = i+.333
        if converted_grade!=grade_num:
            print("Erroneous conversion: " + grade_str + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all plus grades")
    print("Testing minus grades")
    for i in range(test_num):
        grade_str = grade_base + str(i) + '-'
        converted_grade = grade_to_number(grade_str)
        grade_num = i-.333
        if converted_grade!=grade_num:
            print("Erroneous conversion: " + grade_str + " got converted to " + converted_grade)
            break
        if i==test_num-1:
            print("...Succesfully converted all minus grades")
    




if __name__ == "__main__":
    main()