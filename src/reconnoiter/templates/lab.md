# Assignment Feedback

Hi, {{student}}! Here's the calculated score for your assignment. {{^review}}It appears that you're missing your code review; not completing this greatly impacts your score! Be sure to complete it before the deadline in the future.{{/review}}

{{#token}}{{message}}{{/token}}

|Category |Score |
|:--------|:-----|
|Programming|{{#programming}}{{score}}{{/programming}} |
|Writing |{{#writing}}{{score}}{{/writing}} |
|Code Review|{{#review}}{{score}}{{/review}} |

## Programming 

{{#programming}}
{{feedback}}
{{/programming}}

## Writing

{{#writing}}
{{feedback}}
{{/writing}}

## Code Review

{{#review}}
{{feedback}}
{{/review}}