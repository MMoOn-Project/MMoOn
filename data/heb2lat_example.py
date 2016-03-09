#!/usr/bin/python3

import heb2lat

text = "hallo äöü ÄÖÜ HALLO לכד אָכּלֻץ אָאּגּהּ ְ ◌ שׁ שׂ ש"
text2 = "Schulter כָּתֵף"
text2 = "דבר"
trans = heb2lat.heb2lat(text);
print("\n")
trans2 = heb2lat.heb2lat(text2);

print(text)
print(trans)

print(text2)
print(trans2)

heb = heb2lat.lat2heb("D8iB8mRtH-")
print (heb)
