from fastavro.schema import load_schema

OPEN_ACTIONS_IDX01_FILE_TMPLT       = 'actions_open_idx01-{}.avro'
OPEN_ACTIONS_FILE_TMPLT             = 'actions_open-{}.avro'
OPEN_INCIDENTS_FILE_TMPLT           = 'incidents_open-{}.avro'
CLOSED_ACTIONS_IDX01_FILE_TMPLT     = 'actions_closed_idx01-{}.avro'
CLOSED_ACTIONS_FILE_TMPLT           = 'actions_closed-{}.avro'
CLOSED_INCIDENTS_FILE_TMPLT         = 'incidents_closed-{}.avro'


SCHEMA_DIRECTORY                    = "./pyclick/etl/"
INCIDENTS_SCHEMA_FILE               = SCHEMA_DIRECTORY + "incidents.avsc"
ACTIONS_SCHEMA_FILE                 = SCHEMA_DIRECTORY + "actions.avsc"
ACTIONS_IDX01_SCHEMA_FILE           = SCHEMA_DIRECTORY + "actions_idx01.avsc"
OFFERINGS_SCHEMA_FILE               = SCHEMA_DIRECTORY + "offerings.avsc"
ITEMS_SCHEMA_FILE                   = SCHEMA_DIRECTORY + "items.avsc"
SUPPLIERS_SCHEMA_FILE               = SCHEMA_DIRECTORY + "suppliers.avsc"
USERS_SCHEMA_FILE                   = SCHEMA_DIRECTORY + "users.avsc"
ASSYST_USERS_SCHEMA_FILE            = SCHEMA_DIRECTORY + "assyst_users.avsc"
SCHEDULES_SCHEMA_FILE               = SCHEMA_DIRECTORY + "schedules.avsc"
CONSOLIDATED_INCIDENT_SCHEMA_FILE   = SCHEMA_DIRECTORY + "consolidated_incident.avsc"

INCIDENTS_SCHEMA                    = load_schema( INCIDENTS_SCHEMA_FILE     )
ACTIONS_SCHEMA                      = load_schema( ACTIONS_SCHEMA_FILE       )
ACTIONS_IDX01_SCHEMA                = load_schema( ACTIONS_IDX01_SCHEMA_FILE )
OFFERINGS_SCHEMA                    = load_schema( OFFERINGS_SCHEMA_FILE     )
ITEMS_SCHEMA                        = load_schema( ITEMS_SCHEMA_FILE         )
SUPPLIERS_SCHEMA                    = load_schema( SUPPLIERS_SCHEMA_FILE     )
USERS_SCHEMA                        = load_schema( USERS_SCHEMA_FILE         )
ASSYST_USERS_SCHEMA                 = load_schema( ASSYST_USERS_SCHEMA_FILE  )
SCHEDULES_SCHEMA                    = load_schema( SCHEDULES_SCHEMA_FILE     )

