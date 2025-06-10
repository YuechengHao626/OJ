# 1. Microservice Architecture for OpenJudge

Date: 2025-05-05

## Status

Accepted

## Summary

In the context of delivering a web application,
facing security, scalability and deployability requirements and team's familiarity with different frameworks, 
we decided to implement the system using microservices architecture,
to achieve good scalability and deployability while accommodating different skillsets,
accepting potential complexity due to communication between services.

## Context

- The system is delivered as a web application.
- The system prioritises security, scalability and deployability.
- Some team members prefer development using Django, while others prefer Flask.

## Decision

The team decided to implement the system using microservice architecture. The chosen architecture allows each service of openJudge to scale quickly and effectively, allowing the service to handle various loads within reasonable time. It also allows each service to be deployed inidvidually without disrupting other services, improving deployability. While the architecture requires protection for multiple services, each service can have customised security measures.

At the time of writing, OpenJudge's user management service will be written in Flask, while the submission management service will be written in Django. This decision allows team members to be assigned to developing services based on their familiar frameworks. Since microservice architecture will containerise services individually, this allows team members to develop their services using their familiar frameworks and communicate with other services using well-defined APIs.

## Consequences

**Advantages:**
- Fulfills two important quality attributes greatly, which are scalability and deployability.
- Accommodates each team member's preferences in development.
- Separation of concerns, as services are divided based on user and submission management.

**Neutral:**
- Requires additional security measures for each service, increasing complexity but improving overall system security.

**Disadvantages:**
- Additional complexity for the system intorduced by communication between services.
- Need to think about how to communicate between services.

## Alternatives Considered

**Serverless Architecture:**
- Serverless architecture was considered due to good scalability and deployability, but offers less control over security.
- Will need further discussions during team meetings to assess viability.
