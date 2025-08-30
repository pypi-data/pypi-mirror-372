from string import Template

AUTOCREATE_OUTPUT_TEMPLATE = Template(
    """
$subject
$subject_line

Description
$description_line
$description


Associated events 
$associated_events_line
$associated_events
"""
)
