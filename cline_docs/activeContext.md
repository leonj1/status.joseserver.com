# activeContext.md

## Plan to Fix Failing Test

### Issue

The test `test_get_recent_incidents_latest_per_service` is failing because the `/incidents/recent` endpoint returns all incidents for a service instead of only the latest incident per service.

The assertion `assert len(service_a_incidents) == 1` fails because `service_a_incidents` has a length of 3 instead of 1.

### Analysis

- The `/incidents/recent` endpoint currently retrieves recent incidents without grouping by service or filtering to the most recent incident per service.
- To fix the test, we need to modify the endpoint to return only the latest incident for each service.

### Solution

1. **Modify Imports in `src/app/main.py`**:

   Add the necessary SQLAlchemy functions to support grouping and aggregation.

   ```python
   from sqlalchemy import select, desc, func, and_
   ```

2. **Update the Query in `/incidents/recent` Endpoint**:

   Adjust the query to select the latest incident per service using a subquery.

   ```python
   subquery = (
       select(
           Incident.service,
           func.max(Incident.created_at).label('max_created_at')
       ).group_by(Incident.service).subquery()
   )

   query = (
       select(Incident)
       .join(
           subquery,
           and_(
               Incident.service == subquery.c.service,
               Incident.created_at == subquery.c.max_created_at
           )
       )
   )

   result = await db.execute(query)
   incidents = result.scalars().all()
   ```

3. **Test the Changes**:

   Run `test_get_recent_incidents_latest_per_service` to confirm that it now passes.

### Next Steps

- Verify that other tests are still passing to ensure no regressions.
- Review the updated endpoint for performance considerations.
- Update any relevant documentation to reflect the changes.