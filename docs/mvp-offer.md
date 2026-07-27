# MVP Offer — Business Knowledge Base Agent

## Problem

Your team has useful information spread across PDFs, policies, FAQs, product docs, support notes, and website pages. Customers or employees ask repeated questions, and answers are inconsistent or slow.

## Solution

I build a small AI knowledge base assistant that answers questions from your business documents, cites the supporting sources, and refuses when the documents do not contain enough information.

## MVP scope

Timeline:
1–2 weeks for a small first version, depending on document quality and access.

Deliverables:
- Document ingestion for selected files or pages
- Chat endpoint or simple web widget
- Answers grounded in provided documents
- Source citations
- Basic refusal behavior
- Small evaluation set of test questions
- Cost and latency logging
- Short handover explaining limitations and maintenance

## Good fit

This is a good fit if:
- you have repeated support/internal questions
- answers already exist in documents
- documentation is reasonably current
- you want a scoped MVP, not a giant automation platform

## Not a good fit

This is not a good fit if:
- answers require complex human judgment
- documents are outdated or contradictory
- the business expects zero hallucination
- the workflow requires deep integrations from day one
- sensitive answers need legal, medical, or financial approval

## Limitations

This system does not eliminate hallucination. It reduces risk by retrieving business-owned context, citing sources, validating answers, and refusing when evidence is insufficient.

## First discovery questions

1. What questions are people repeatedly asking?
2. Where do the correct answers currently live?
3. Which documents are trusted and up to date?
4. Which topics should the assistant refuse to answer?
5. Who reviews failed or uncertain answers?
6. What would count as a successful MVP after two weeks?