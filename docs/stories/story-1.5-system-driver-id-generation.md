# Story 1.5: System Driver ID Generation

**Epic**: Epic 1 - User Authentication & Account Management  
**Story ID**: US1.5  
**Priority**: P2 (Medium)  
**Story Points**: 3  
**Status**: 📋 NOT STARTED

## User Story
**As a system, I want to auto-generate unique driver IDs so that each driver has a traceable identifier**

## Acceptance Criteria
- [ ] System generates IDs in format DRV-XXXYYY
- [ ] XXX is sequential driver number within fleet
- [ ] YYY is fleet identifier code
- [ ] IDs are unique across entire system
- [ ] ID generation is atomic and thread-safe

## Technical Requirements
- [ ] Implement atomic ID generation with database sequences
- [ ] Create fleet-based numbering system
- [ ] Add uniqueness constraints in database
- [ ] Handle concurrent registration scenarios

## Implementation Plan

### Phase 1: Fleet Code System
- [ ] Create fleet code generation algorithm
- [ ] Implement fleet code uniqueness validation
- [ ] Add fleet code to fleet management system
- [ ] Create fleet code lookup service

### Phase 2: Driver Number Sequences
- [ ] Create database sequences for each fleet
- [ ] Implement atomic sequence increment
- [ ] Add sequence reset functionality
- [ ] Handle sequence overflow scenarios

### Phase 3: Driver ID Generation Service
- [ ] Create driver ID generation service
- [ ] Implement format validation
- [ ] Add ID uniqueness checking
- [ ] Create ID reservation system

### Phase 4: Concurrent Handling
- [ ] Implement database-level locking
- [ ] Add retry logic for conflicts
- [ ] Create transaction isolation
- [ ] Handle high-concurrency scenarios

## Driver ID Format Specification

### Format: `DRV-XXXYYY`
- **DRV**: Fixed prefix for all driver IDs
- **XXX**: Sequential number within fleet (001-999)
- **YYY**: Fleet identifier code (3 alphanumeric characters)

### Examples:
- `DRV-001ABC` - First driver in fleet ABC
- `DRV-002ABC` - Second driver in fleet ABC
- `DRV-001XYZ` - First driver in fleet XYZ

### Fleet Code Generation:
- Use combination of letters and numbers
- Avoid confusing characters (0, O, I, 1)
- Ensure global uniqueness
- Case-insensitive comparison

## Database Schema

```sql
-- Fleet sequences table
CREATE TABLE fleet_driver_sequences (
    fleet_id UUID PRIMARY KEY REFERENCES fleets(id),
    current_number INTEGER DEFAULT 0,
    max_number INTEGER DEFAULT 999,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Driver ID reservations (for handling concurrency)
CREATE TABLE driver_id_reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    driver_id VARCHAR(20) UNIQUE NOT NULL,
    fleet_id UUID REFERENCES fleets(id),
    reserved_by VARCHAR(100), -- session/process identifier
    reserved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '5 minutes'
);

-- Add unique constraint to driver_profiles
ALTER TABLE driver_profiles 
ADD CONSTRAINT unique_driver_id UNIQUE (driver_id);

-- Add fleet code to fleets table
ALTER TABLE fleets 
ADD COLUMN fleet_code VARCHAR(3) UNIQUE NOT NULL;
```

## Driver ID Generation Algorithm

```python
def generate_driver_id(fleet_id: str) -> str:
    """
    Generate unique driver ID for fleet
    
    Args:
        fleet_id: Fleet UUID
        
    Returns:
        Generated driver ID in format DRV-XXXYYY
        
    Raises:
        FleetCapacityError: If fleet has reached maximum drivers
        ConcurrencyError: If unable to generate after retries
    """
    
    # 1. Get fleet code
    fleet = get_fleet_by_id(fleet_id)
    fleet_code = fleet.fleet_code
    
    # 2. Get next sequence number atomically
    with database_transaction():
        sequence = get_or_create_fleet_sequence(fleet_id)
        
        if sequence.current_number >= sequence.max_number:
            raise FleetCapacityError(f"Fleet {fleet_code} has reached maximum capacity")
        
        next_number = sequence.current_number + 1
        update_fleet_sequence(fleet_id, next_number)
    
    # 3. Format driver ID
    driver_id = f"DRV-{next_number:03d}{fleet_code}"
    
    # 4. Reserve ID to prevent conflicts
    reserve_driver_id(driver_id, fleet_id)
    
    return driver_id
```

## Concurrency Handling

### Database-Level Protection:
- Use database sequences for atomic increments
- Implement row-level locking on fleet sequences
- Add unique constraints on driver IDs
- Use transaction isolation levels

### Application-Level Protection:
- Implement retry logic with exponential backoff
- Add ID reservation system with expiration
- Use distributed locks for high-concurrency scenarios
- Monitor and alert on generation failures

### Error Handling:
- Handle sequence overflow gracefully
- Retry on concurrent modification errors
- Clean up expired reservations automatically
- Log all generation attempts for debugging

## Testing Strategy

### Unit Tests:
- Test ID format validation
- Test sequence increment logic
- Test fleet code generation
- Test error handling scenarios

### Integration Tests:
- Test concurrent driver registration
- Test sequence overflow handling
- Test ID uniqueness across system
- Test reservation cleanup

### Load Tests:
- Simulate high-concurrency registration
- Test system under peak load
- Measure ID generation performance
- Validate no duplicate IDs generated

## Performance Considerations

### Optimization Strategies:
- Cache fleet codes in memory
- Pre-allocate ID ranges for high-volume fleets
- Use connection pooling for database access
- Implement async ID generation where possible

### Monitoring:
- Track ID generation latency
- Monitor sequence utilization per fleet
- Alert on generation failures
- Dashboard for fleet capacity planning

## Definition of Done
- [ ] Driver ID generation service implemented
- [ ] Atomic sequence management working
- [ ] Concurrency handling tested and verified
- [ ] Fleet code system operational
- [ ] Uniqueness constraints enforced
- [ ] Performance testing completed
- [ ] Error handling comprehensive
- [ ] Monitoring and alerting configured
- [ ] Documentation updated
- [ ] Integration tests passing

## Dependencies
- [ ] Fleet management system
- [ ] Database sequence support
- [ ] Transaction management
- [ ] Monitoring infrastructure

## Risks & Mitigation
- **Risk**: ID generation bottleneck under high load
  - **Mitigation**: Pre-allocation and caching strategies
- **Risk**: Sequence corruption in database failures
  - **Mitigation**: Backup and recovery procedures
- **Risk**: Fleet capacity limits reached
  - **Mitigation**: Monitoring and capacity planning

## Notes
- Maximum 999 drivers per fleet (can be increased if needed)
- Fleet codes are case-insensitive but stored uppercase
- ID reservations expire after 5 minutes to prevent deadlocks
- System supports up to 46,656 unique fleet codes (36^3)
- Driver IDs are immutable once assigned
