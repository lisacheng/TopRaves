from selenium import webdriver
import sys

#parse time stamp and return flloat
#1 hour = 1.0, 1 hour 15 minutes = 1.25
def parse_time_stamp(ts):
    ts = str(ts)
    ts = ts.split()

    if ts[2] == "hours":
        return float(ts[1])
    elif ts[2] == "hour":
        return float(1)
    elif ts[2] == "minutes":
        return float(ts[1])/60
    elif ts[2] == "minute":
        return float(1)/60
    elif ts[2] == "seconds":
        return float(ts[1])/360
    elif ts[2] == "second":
        return float(1)/360
    else:
        return 0

#parse tagline for subreddit
def parse_sub_reddit(sr):
    sub = sr.split()
    return sub[len(sub)-1]

#parse comment line
def parse_comments(c):
    comments = c.split()
    if(comments[0] == "comment"):
        return 0
    else:
        return int(comments[0])

#return rank
def get_rank(we):
    rank = we.find_element_by_xpath(".//*[@class = 'rank']").text
    rank = rank.encode("utf_8")
    return int(rank)

#return score as upvotes - downvotes
def get_score(we):
    down_votes = int(we.get_attribute('data-downs'))
    up_votes = int(we.get_attribute('data-ups'))
    return up_votes - down_votes

#return time stamp as float
def get_time_stamp(we):
    tag_line = we.find_element_by_xpath(".//*[@class = 'tagline']").text
    tag_line = tag_line.encode("utf_8")
    return parse_time_stamp(tag_line)

#return subreddit
def get_sub_reddit(we):
    tag_line = we.find_element_by_xpath(".//*[@class = 'tagline']").text
    tag_line = tag_line.encode("utf_8")
    return parse_sub_reddit(tag_line)

#return number of comments
def get_comments(we):
    comments_line = we.find_element_by_xpath(".//*[@class = 'first']")
    comments_line = comments_line.find_element_by_xpath("./a").text
    return parse_comments(comments_line)

#return link to comments section
def get_link(we):
    link = we.find_element_by_xpath(".//*[@class = 'first']")
    link = link.find_element_by_xpath("./a").get_attribute('href')
    return link.encode("utf_8")

#return driver
def get_driver():
    driver = webdriver.Firefox()
    driver.get("http://www.reddit.com")
    return driver

#return all threads on current page
def get_page_info(driver):
    site_table = driver.find_element_by_xpath("//*[@id = 'siteTable']")
    div_tags = site_table.find_elements_by_xpath("./div[contains(@class, 'thing')]")
    page = []

    i = 0
    while i < len(div_tags):
        rank = get_rank(div_tags[i])
        score = get_score(div_tags[i])
        time = get_time_stamp(div_tags[i])
        sub = get_sub_reddit(div_tags[i])
        comments = get_comments(div_tags[i])
        link = get_link(div_tags[i])
        page.append([rank, score, comments, time, sub, link])
        i = i + 1
    
    return page

#return all threads on all pages
def get_candidates(pages):

    candidates = []
    driver = get_driver()
    i = 0
    while i < pages:
        print ("Fetching page " + str(i+1) + "...")
        page = get_page_info(driver)
        candidates = candidates + page
        next_page = driver.find_element_by_xpath("//*[@rel='nofollow next']")
        next_page.click()
        i = i + 1
    print ""
    driver.quit()

    return candidates

#partition for quicksort
def partition(List, start, end, col_index):
    pivot = List[start][col_index]
    left = start+1
    right = end
    done = False
    while not done:
        while left <= right and List[left][col_index] <= pivot:
            left = left + 1
        while List[right][col_index] >= pivot and right >=left:
            right = right -1
        if right < left:
            done= True
        else:
            # swap places
            temp=List[left]
            List[left] = List[right]
            List[right] = temp
    # swap start with myList[right]
    temp = List[start]
    List[start] = List[right]
    List[right] = temp
    return right

#quicksort list of lists
def quick_sort(List, start, end, col_index):
    if start < end:
        # partition the list
        pivot = partition(List, start, end, col_index)
        # sort both halves
        quick_sort(List, start, pivot-1, col_index)
        quick_sort(List, pivot+1, end, col_index)
    return List

#filter candidates as specified by user. return filtered list
def filter_candidates(List, sort_by, max_points, max_comments, max_hours):
    #sorting by coloumn
    if sort_by.lower() == "points":
        col_index = 1
    elif sort_by.lower() == "comments":
        col_index = 2
    elif sort_by.lower() == "time":
        col_index = 3
    elif sort_by.lower() == "sub":
        col_index = 4
    else:
        col_index = 0
    List = quick_sort(List, 0, len(List)-1, col_index)

    #getting filter criteria
    if not(max_points):
        max_points = sys.maxint
    if not(max_comments):
        max_comments = sys.maxint
    if not(max_hours):
        max_hours = sys.maxint
    i = 0

    #filtering list
    while i < len(List):
        if List[i][1] > max_points or List[i][2] > max_comments or List[i][3] > max_hours:
            List.pop(i)
        else:
            i = i + 1
    return List

#main program
def main(pages, sort_by, max_points, max_comments, max_hours):
    candidates = get_candidates(pages)
    results = filter_candidates(candidates, sort_by, max_points, max_comments, max_hours)
    print "{0:5s} {1:7s} {2:9s} {3:6s} {4:25s} {5:s}".format('Rank', 'Points', 'Comments', 'Hours', 'Sub', 'Link')
    for ent in results:
        print "{0:5s} {1:7s} {2:9s} {3:6s} {4:25s} {5:s}".format(str(ent[0]), str(ent[1]), str(ent[2]), str(round(ent[3], 2)), ent[4], ent[5])


#number of pages to fetch
pages = 5
#sort list by 'rank', 'points', 'comments', 'time', or 'sub'. defaults to 'rank' if invalid, not case sensitive
#sorts in descending order
sort_by = "rank"
#maximum points as int
max_points = None
#maximin comments as int
max_comments = None
#maximum hours as float. 1 hour 15 minutes = 1.25
max_hours = 2
#run program
main(pages, sort_by, max_points, max_comments, max_hours)

                      

