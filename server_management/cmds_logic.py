
def hex_color_to_rgb(hex_str:str):
    nums =hex_str.strip('#')#if i would convert it here it would loose its structure bcs dd could turn into more than two positions but in the str it is always 2 positions
    r = int(nums[0:2],16)#first one so pos 0 included second isn't so from 0 to and without 2 so from 0 to 1
    g = int(nums[2:4], 16)
    b = int(nums[4:6],16)
    return r,g,b

def full_rgb(r:int,g:int,b:int):
    if not all(isinstance(char,int) for char in (r,g,b)):
        return None
    rgb = str(r)
    rgb += str(g)
    rgb += str(b)
    return int(rgb)

def other_rbg(r:int,g:int,b:int):
    if not all(isinstance(char,int) for char in (r,g,b)):
        return None
    #rgb is 24 bit each letter occupies max 8 bit and so to combine them we do like basecly a += so like we say r move 16 to the left then move g 8 to the left and then b stays at his place and 
    # so now we can say from the first positon (from left to right) to the 8th position we have the value r from the 8th to the 16th position we have the value of g and the rest is the value of b
    r = r << 16
    g = g << 8
    b = b
    return r+g+b # its like if you have 40 40 94 its 40 00 00 + 40 00 + 94 = 40 40 94 because they are all at different positions
