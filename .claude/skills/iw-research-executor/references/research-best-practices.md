# Research Gathering Best Practices

## Academic Paper Research

### Finding Papers:
- **Google Scholar**: `site:scholar.google.com <topic>`
- **arXiv**: `site:arxiv.org <field> <keywords>`
- **PubMed**: For medical/biological research
- **ACM Digital Library**: For computer science
- **IEEE Xplore**: For engineering/technology

### Extracting Information:
1. **Read abstract first** - does it address research questions?
2. **Check methodology** - is it sound and relevant?
3. **Extract key findings** - what did they discover?
4. **Note limitations** - what didn't they address?
5. **Capture citations** - in simple format (Author, Year, Title, URL)

### Quality Indicators:
- Peer-reviewed publications preferred
- Recent publications (last 5 years) unless historical context needed
- Highly-cited papers indicate impact
- Check for conflicts of interest
- Cross-reference findings across multiple papers

### Simple Citation Format:
```markdown
[Author et al., Year] "Paper Title" - URL
- Key contribution: Brief description of main finding
```

## Code Repository Research

### Finding Repos:
- **GitHub search** with filters (stars, recent activity, language)
- **Awesome lists** for curated collections
- **Official organization repos** (e.g., facebook/react, vercel/next.js)
- Search by topic, language, and popularity

### Extracting Information:
1. **Start with README** - understand purpose and architecture
2. **Check documentation** - how is it used?
3. **Examine key files** - implementation patterns
4. **Look at tests** - usage examples
5. **Note file paths and line numbers** for code examples

### Quality Indicators:
- Active maintenance (recent commits)
- Good documentation
- Test coverage
- Community adoption (stars, forks, issues)
- Clear code organization

### Code Reference Format:
```markdown
[Repo Name] org/repo - URL
- Examined: path/to/file.js:45-80
- Pattern: Brief description of what pattern was found
- Example:
  ```language
  // From: path/to/file.js:45-50
  code snippet here
  ```
```

## Technical Documentation Research

### Finding Docs:
- Official documentation sites
- API references
- Developer guides
- Architecture decision records (ADRs)
- Release notes and changelogs

### Extracting Information:
1. **Overview/getting started** - basic concepts
2. **Core concepts** - how it works
3. **API reference** - specific capabilities
4. **Best practices** - recommended patterns
5. **Limitations/gotchas** - what to avoid

### Quality Indicators:
- Official or maintained by core team
- Up-to-date (matches current version)
- Comprehensive coverage
- Includes examples
- Clear and well-organized

### Documentation Reference Format:
```markdown
[Technology Name] Official Documentation - URL
- Section: Section name or path
- Key points:
  - Point 1
  - Point 2
- Example: Brief code or usage example
```

## Blog Posts and Articles

### Finding Articles:
- Technical blogs (dev.to, Medium, personal blogs)
- Company engineering blogs
- Community forums and discussions
- Tutorial sites

### Extracting Information:
1. **Check author credibility** - experience and expertise
2. **Check publication date** - is it current?
3. **Extract key insights** - practical lessons learned
4. **Note examples** - real-world use cases
5. **Verify claims** - cross-check with other sources

### Quality Indicators:
- Author has relevant experience
- Article is recent or timeless
- Includes practical examples
- Backed by evidence or references
- Clear and well-written

### Article Reference Format:
```markdown
[Author Name] "Article Title" - URL
- Published: Date (if available)
- Key insights:
  - Insight 1
  - Insight 2
```

## Thematic Organization

### Identify Themes:
- Look for **recurring concepts** across sources
- Group **related findings** together
- Note **agreements and contradictions** between sources
- Identify **patterns and trends**

### Common Theme Types:
- **Implementation patterns** - how things are built
- **Performance considerations** - speed, efficiency, scalability
- **Security best practices** - protecting against threats
- **Common pitfalls** - mistakes to avoid
- **Evolution over time** - how approaches have changed
- **Trade-offs** - advantages vs disadvantages

### Theme Organization Structure:
```markdown
## Theme Name

### Subtopic (Sources: #1, #3, #5)
- Finding from source #1: Description with context
- Finding from source #3: Additional perspective
- Code example from source #5:
  ```language
  // From: repo/path/file.ext:line-range
  code snippet
  ```

**Synthesis:**
How do these findings relate? What patterns emerge? Any contradictions?

### Another Subtopic (Sources: #2, #4)
...
```

### Cross-Reference Sources:
- **Link findings to multiple sources** - show corroboration
- **Show how sources support each other** - build comprehensive view
- **Highlight contradictions** - note where sources disagree
- **Build evidence hierarchies** - strong evidence vs weak evidence

### Example:
```markdown
## Authentication Security Patterns

### Token Storage Strategies (Sources: #1, #3, #5)
- Source #1 (Paper): httpOnly cookies prevent XSS attacks on tokens
- Source #3 (Documentation): Cookies with httpOnly flag cannot be accessed via JavaScript
- Source #5 (Code repo): Implementation example from Next.js auth library

**Synthesis:**
All sources agree: httpOnly cookies are the recommended approach for JWT storage
in web applications. This is a well-established security pattern with broad consensus.

### Session vs Token Authentication (Sources: #2, #4, #6)
- Source #2 (Article): Token auth better for microservices and mobile apps
- Source #4 (Paper): Session auth has lower overhead for traditional web apps
- Source #6 (Code repo): Hybrid approaches combine both strategies

**Synthesis:**
Contradictory recommendations based on context. Choice depends on:
- Application architecture (monolith vs microservices)
- Client types (web only vs multi-platform)
- Performance requirements
- Security requirements
```

## Research Quality Checklist

### Coverage:
- [ ] Each research question addressed by multiple sources
- [ ] Variety of source types (papers, code, docs, articles)
- [ ] Recent and historical sources for context
- [ ] Both theoretical and practical perspectives

### Organization:
- [ ] Findings organized by theme, not just by source
- [ ] Cross-references between related findings
- [ ] Contradictions noted and analyzed
- [ ] Patterns and trends identified

### Attribution:
- [ ] All sources properly cited
- [ ] Code examples include file:line references
- [ ] Quotes attributed to original source
- [ ] Dates and versions noted where relevant

### Completeness:
- [ ] No major gaps in coverage
- [ ] Sufficient depth for each theme
- [ ] Limitations acknowledged
- [ ] Areas for further research identified

## Tips for Effective Research

### Start Broad, Then Narrow:
1. Begin with overview sources (docs, introductory articles)
2. Identify key concepts and themes
3. Deep dive into specific areas
4. Cross-reference and validate findings

### Balance Breadth and Depth:
- Don't go too deep on one source before exploring others
- Survey multiple perspectives before committing to one view
- Return to deeper investigation after initial survey

### Document As You Go:
- Add sources immediately using `add_source.py`
- Add findings incrementally using `add_finding.py`
- Don't wait until the end to organize
- Update themes as new patterns emerge

### Quality Over Quantity:
- 5 high-quality sources better than 20 superficial ones
- Deep understanding trumps broad coverage
- Synthesis matters more than collection

### Critical Evaluation:
- Question assumptions in sources
- Look for bias or conflicts of interest
- Verify claims across multiple sources
- Distinguish fact from opinion
- Note confidence levels (established vs emerging)

## Common Pitfalls to Avoid

### Research Pitfalls:
- ❌ Relying on a single source type
- ❌ Not verifying claims across sources
- ❌ Ignoring publication dates
- ❌ Accepting claims without evidence
- ❌ Confirmation bias (only seeking supporting evidence)

### Organization Pitfalls:
- ❌ Organizing by source instead of theme
- ❌ Not cross-referencing findings
- ❌ Ignoring contradictions
- ❌ Poor attribution
- ❌ Losing track of sources

### Practical Solutions:
- ✅ Use multiple source types for each question
- ✅ Cross-check important claims
- ✅ Note publication dates and versions
- ✅ Seek contradicting viewpoints
- ✅ Organize thematically from the start
- ✅ Use scripts to maintain structure
- ✅ Document sources immediately
