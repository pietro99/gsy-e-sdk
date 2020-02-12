Feature: Device Tests

Scenario: API client can connect successfully to a load device and perform all operations
   Given redis container is started
   And d3a container is started using setup file strategy_tests.external_devices
   When the external client is started with test_load_connection
   Then the external client is connecting to the simulation until finished
   And the external client does not report errors
   And the energy bills of the load report the required energy was bought by the load

Scenario: API client can connect successfully to a PV device and perform all operations
   Given redis container is started
   And d3a container is started using setup file strategy_tests.external_devices
   When the external client is started with test_pv_connection
   Then the external client is connecting to the simulation until finished
   And the external client does not report errors

Scenario: External ESS agent not allowed to overcharge the Storage State
   Given redis container is started
   And d3a container is started using setup file strategy_tests.external_ess_bids
   When the external client is started with test_ess_bid_connection
   Then the external client is connecting to the simulation until finished
   And the external client does not report errors
#   And the external failed to place bids beyond the full capacity of storage
