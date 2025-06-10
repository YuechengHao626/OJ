# 3. Combined Frontend and Backend for OpenJudge

Date: 2025-05-19

## Status

Accepted

## Summary

In the context of completing OpenJudge on time,
facing development complexity and insufficient time for the team to learn alternatives,
we decided to combine the frontend and backend of OpenJudge in each service,
to achieve simplified development and reduced time requirements,
accepting that it may not meet industrial standards for microservice architecture, and prevents frontend delivery to scale independently.

## Context

- The team have no experience in serving frontend web pages independently in Flask apps as of now.
- The team is juggling between this project and next week's presentation.
- The team do not have enough time to learn additional knowledge to serve frontend as a spearate service.

## Decision

The team decided to implement OpenJudge to handle frontend delivery and backend processing together in each service. For instance, each service will serve the frontend pages and use API endpoints to deliver required features. This simplifies our development effort as we can just focus on the two main services, reducing time and effort needed to complete OpenJudge on time.

At the time of writing, we have decided to only have two main services that handles data processing and page delivery, and no additional services to handle frontend page delivery. This reduces the number of services that we need to develop, saving us time to refine and complete the two main services of OpenJudge.

## Consequences

**Advantages:**
- Reduces complexity of overall project, as we only need to think about communication between two services.
- Saves development time, as we only need to develop two services.
- Guarantess that the required pages are served correctly within a service's function.

**Disadvantages:**
- Does not allow independent scaling for frontend delivery, although it is a necessary compromise.
