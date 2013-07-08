=================
API Documentation
=================

Meetings
========

You can get the last 30 meetings via the ``/meetings`` endpoint. This will include URLs to the detailed meeting endpoint.


Meeting
=======

At ``/meetings/<meeting_id>`` you will find detailed information about a meeting including all the agenda items including links
to documents. Transcription details will be included if available.

* What about a condensed form without transcripts? Agenda items could then be referenced individually at ``/meetings/<meeting_id>/<agenda_item>``
*

Documents
=========

The ``/documents/<document_id>`` endpoint will give you all information about a document. As a document can be used in multiple meetings
it's a separate namespace. The document will also include links to meetings where it was discussed and a link to attachments or the PDF version of it.





