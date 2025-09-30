# Jira Story: B2C Diner Tracking Process Enhancement

## Story Title
**Implement Universal B2C Diner Tracking Process Across Merchant and Diner Programs**

## Story Type
Epic / Feature

## Priority
High

## Story Points
13

---

## Summary
Currently there's no tracking in place for day-to-day sends in the B2C Diner program, and we need to establish a universal tracking process consistent across all programs. This enhancement will mirror the current B2C Diner tracking process across both Merchant and Diner programs, with API support for UTM parameter alignment in email communications.

---

## Problem Statement
- **Current State**: No tracking exists for day-to-day B2C Diner program communications
- **Impact**: Inability to measure campaign effectiveness, user engagement, and ROI
- **Goal**: Establish consistent tracking methodology across all programs (Merchant and Diner)

---

## Acceptance Criteria

### AC1: Universal Tracking Implementation
- [ ] Implement tracking system that mirrors existing B2C Diner tracking process
- [ ] Ensure consistency across both Merchant and Diner programs
- [ ] Track day-to-day sends and user interactions

### AC2: UTM Parameter Integration
- [ ] Implement UTM parameter structure for email campaigns:
  - `utm_source = "utm_source=braze"`
  - `utm_medium = "utm_medium=email_owned"`
  - `utm_campaign = "utm_campaign=" | append: canvas.name`
  - `utm_content = "utm_content=" | append: campaign.name | replace: "&", "_"`
- [ ] Ensure UTM parameters are properly encoded and formatted

### AC3: API Integration for Email Templates
- [ ] Set up APIs to align UTMs with links in email templates
- [ ] Implement data extraction from Braze in usable format
- [ ] Ensure seamless integration with existing email template system

### AC4: Data Collection and Reporting
- [ ] Capture and store tracking data for analysis
- [ ] Implement reporting mechanism for campaign performance
- [ ] Ensure data consistency and accuracy across programs

---

## Technical Requirements

### UTM Parameter Implementation
```liquid
{% assign utm_source = "utm_source=braze" %}
{% assign utm_medium = "utm_medium=email_owned" %}
{% assign utm_campaign = "utm_campaign=" | append: canvas.name %}
{% assign utm_content = "utm_content=" | append: campaign.name | replace: "&", "_" %}
{% comment %} Replaces & with _ {% endcomment %}
```

### API Specifications
- **Purpose**: Extract data from Braze in usable format for Diner email templates
- **Requirements**: 
  - UTM parameter alignment with email links
  - Data formatting for template consumption
  - Error handling and validation

### Integration Points
- Braze email platform
- Existing Merchant program tracking system
- Diner program communication channels
- Analytics and reporting systems

---

## Definition of Done
- [ ] Universal tracking process implemented and tested
- [ ] UTM parameters correctly applied to all email communications
- [ ] API endpoints created and documented
- [ ] Data extraction from Braze working as expected
- [ ] Tracking consistency verified across Merchant and Diner programs
- [ ] Documentation updated with new tracking procedures
- [ ] QA testing completed across all scenarios
- [ ] Performance monitoring in place

---

## Dependencies
- Access to Braze platform configuration
- Existing Merchant program tracking system documentation
- Email template system architecture
- Analytics platform integration capabilities

---

## Risks and Mitigation
| Risk | Impact | Mitigation |
|------|--------|------------|
| UTM parameter conflicts with existing links | Medium | Thorough testing and validation of parameter encoding |
| API performance issues | High | Implement caching and optimize data extraction queries |
| Data inconsistency between programs | High | Establish data validation rules and monitoring |
| Braze integration complexity | Medium | Collaborate with Braze support and review documentation |

---

## Success Metrics
- 100% of day-to-day Diner program sends include tracking parameters
- Consistent tracking data format across Merchant and Diner programs
- Successful UTM parameter application rate > 99%
- API response time < 200ms for data extraction
- Zero data loss during tracking implementation

---

## Additional Notes
- This story focuses on establishing the foundation for comprehensive B2C Diner tracking
- Future enhancements may include advanced analytics and personalization features
- Consider scalability for future program expansions
- Ensure compliance with data privacy regulations

---

## Labels
`b2c-tracking`, `diner-program`, `merchant-program`, `utm-parameters`, `braze-integration`, `email-marketing`

## Components
- Email Marketing Platform
- Analytics System
- API Services
- Data Processing

## Assignee
[To be assigned]

## Reporter
[Your name/team]

## Created Date
September 30, 2025