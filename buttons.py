def create_button(textValue, displayText):
    return "<button class='modelSelectBtn' data-target='%s'><span class='title'>%s</span>&nbsp;</button>"%(str(textValue), str(displayText))

def create_link_button(url, displayText):
    return "<a class='modelSelectBtn' href='%s' target='_blank'><span class='title'>%s</span>&nbsp;</a>"%(str(url), str(displayText))