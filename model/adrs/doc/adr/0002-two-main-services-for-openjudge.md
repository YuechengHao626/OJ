# 2. Two Main Services for OpenJudge

Date: 2025-05-12

## Status

Accepted

## Summary

In the context of delivering OpenJudge with a microservice architecture,
facing development time constraints due to other responsibilities,
we decided to split OpenJudge into two main services, which are user and submission service, developed using whichever framework of our choice, 
to achieve lower development complexity and finish the project on time,
accepting potential complexity within each service.

## Context

- OpenJudge is to be delivered with a microservice architecture.
- Each team member had less than ideal time to work on OpenJudge due to other responsibilities.

## Decision
The team decided to only have two service for OpenJudge. The first service handles user-relared services, such as login, profile details and logout. The second service handles submission-related service, such as fetching submissions of a user and create a new submission. The submission service will communicate with user service to fetch user details. This allows each service to be scaled and deployed independently, while reducing the difficulty of developing OpenJudge's services for the team to achieve timely completion.

At the time of writing, the user service will be written in Flask, while the submission service may be written in Flask or Django, depending on the team member responsible for it. This gives us flexibility in developing the required services using the appropriate framework for our situation, greatly reducing time needed to accomplish the task as we are no longer forced to learn a new framework during development.

## Consequences

**Advantages:**
- Satisfies the required ASRs of OpenJudge.
- Simplifies development effort for the team.
- Reduces time required to complete the project.

**Neutral:**
- May not satisfy industrial standards for microservice architecture.
- May result in bulkier services, as each service will have multiple functions related to user or submission.
