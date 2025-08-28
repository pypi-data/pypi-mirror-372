import re
import xml.etree.ElementTree as ET

def extract_links_from_sitemap(text):
    """
    Given the text content of a sitemap (which may include extra text
    before the XML), extract and return all URLs found in <loc> tags.
    
    Args:
        text (str): The sitemap content as a string.
    
    Returns:
        list: A list of URL strings.
    """
    # Try to find the start of the XML part.
    xml_start = text.find("<urlset")
    if xml_start != -1:
        xml_text = text[xml_start:]
        try:
            # Parse the XML portion.
            tree = ET.fromstring(xml_text)
            
            # Extract namespace if present
            m = re.match(r'\{(.*)\}', tree.tag)
            namespace = m.group(1) if m else ''
            
            links = []
            # Use the namespace (if any) to find each <url> element and its <loc> child.
            for url in tree.findall(f"{{{namespace}}}url"):
                loc = url.find(f"{{{namespace}}}loc")
                if loc is not None and loc.text:
                    links.append(loc.text.strip())
            if links:
                return links
        except ET.ParseError:
            # If XML parsing fails, we’ll fall back to regex.
            pass

    # Fallback: use regex to find all <loc>...</loc> content.
    links = re.findall(r"<loc>(.*?)</loc>", text, re.DOTALL)
    return [link.strip() for link in links if link.strip()]

def chunk_list(lst, max_size):
    """
    Splits `lst` into equal sized sublists such that none exceed `max_size` in length.
    The sublists are as equal as possible in size.

    Args:
        lst (list): The list to be split.
        max_size (int): The maximum size for each sublist.

    Returns:
        list: A list of sublists.
    """
    n = len(lst)
    if n <= max_size:
        return [lst]
    
    # Determine how many chunks are needed.
    number_of_chunks = math.ceil(n / float(max_size))
    # Calculate the floor size of each chunk.
    chunk_size_floor = n // number_of_chunks
    # The remainder tells us how many chunks need one extra element.
    remainder = n % number_of_chunks

    chunks = []
    start = 0
    for i in range(number_of_chunks):
        # Distribute the extra items to the first 'remainder' chunks.
        current_chunk_size = chunk_size_floor + (1 if i < remainder else 0)
        chunks.append(lst[start:start + current_chunk_size])
        start += current_chunk_size
    return chunks