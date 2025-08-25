#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL


CREATE DATABASE radius;
\c radius
CREATE TABLE eduroam_eduroamaccount (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    password VARCHAR(510) NOT NULL,
    comment VARCHAR(510) NOT NULL,
    realm VARCHAR(510) NOT NULL,
    status INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    end_date TIMESTAMP NULL,
    start_date TIMESTAMP NULL,
    username VARCHAR(254) NOT NULL UNIQUE
);

CREATE OR REPLACE VIEW radcheck AS
select
    username AS id,
    username AS UserName,
    'Cleartext-Password' AS attribute,
    password AS Value,
    ':=' AS Op
from
    eduroam_eduroamaccount
where
    (status = 1);
-- create index radcheck_UserName on radcheck (UserName,Attribute);
/*
 * Use this index if you use case insensitive queries
 */
-- create index radcheck_UserName_lower on radcheck (lower(UserName),Attribute);


/*
 * Table structure for table 'radacct'
 *
 */
CREATE TABLE IF NOT EXISTS radacct (
	RadAcctId		bigserial PRIMARY KEY,
	AcctSessionId		text NOT NULL,
	AcctUniqueId		text NOT NULL UNIQUE,
	UserName		text,
	Realm			text,
	NASIPAddress		inet NOT NULL,
	NASPortId		text,
	NASPortType		text,
	AcctStartTime		timestamp with time zone,
	AcctUpdateTime		timestamp with time zone,
	AcctStopTime		timestamp with time zone,
	AcctInterval		bigint,
	AcctSessionTime		bigint,
	AcctAuthentic		text,
	ConnectInfo_start	text,
	ConnectInfo_stop	text,
	AcctInputOctets		bigint,
	AcctOutputOctets	bigint,
	CalledStationId		text,
	CallingStationId	text,
	AcctTerminateCause	text,
	ServiceType		text,
	FramedProtocol		text,
	FramedIPAddress		inet,
	FramedIPv6Address	inet,
	FramedIPv6Prefix	inet,
	FramedInterfaceId	text,
	DelegatedIPv6Prefix	inet,
	Class			text
);
-- This index may be useful..
-- CREATE UNIQUE INDEX radacct_whoson on radacct (AcctStartTime, nasipaddress);

-- For use by update-, stop- and simul_* queries
CREATE INDEX radacct_active_session_idx ON radacct (AcctUniqueId) WHERE AcctStopTime IS NULL;

-- Add if you you regularly have to replay packets
-- CREATE INDEX radacct_session_idx ON radacct (AcctUniqueId);

-- For backwards compatibility
-- CREATE INDEX radacct_active_user_idx ON radacct (AcctSessionId, UserName, NASIPAddress) WHERE AcctStopTime IS NULL;

-- For use by onoff-
CREATE INDEX radacct_bulk_close ON radacct (NASIPAddress, AcctStartTime) WHERE AcctStopTime IS NULL;

-- and for common statistic queries:
CREATE INDEX radacct_start_user_idx ON radacct (AcctStartTime, UserName);

-- and, optionally
-- CREATE INDEX radacct_stop_user_idx ON radacct (acctStopTime, UserName);

-- and for Class
CREATE INDEX radacct_calss_idx ON radacct (Class);




/*
 * Table structure for table 'radgroupcheck'
 */
CREATE TABLE IF NOT EXISTS radgroupcheck (
	id			serial PRIMARY KEY,
	GroupName		text NOT NULL DEFAULT '',
	Attribute		text NOT NULL DEFAULT '',
	op			VARCHAR(2) NOT NULL DEFAULT '==',
	Value			text NOT NULL DEFAULT ''
);
create index radgroupcheck_GroupName on radgroupcheck (GroupName,Attribute);

/*
 * Table structure for table 'radgroupreply'
 */
CREATE TABLE IF NOT EXISTS radgroupreply (
	id			serial PRIMARY KEY,
	GroupName		text NOT NULL DEFAULT '',
	Attribute		text NOT NULL DEFAULT '',
	op			VARCHAR(2) NOT NULL DEFAULT '=',
	Value			text NOT NULL DEFAULT ''
);
create index radgroupreply_GroupName on radgroupreply (GroupName,Attribute);

/*
 * Table structure for table 'radreply'
 */
CREATE TABLE IF NOT EXISTS radreply (
	id			serial PRIMARY KEY,
	UserName		text NOT NULL DEFAULT '',
	Attribute		text NOT NULL DEFAULT '',
	op			VARCHAR(2) NOT NULL DEFAULT '=',
	Value			text NOT NULL DEFAULT ''
);
create index radreply_UserName on radreply (UserName,Attribute);
/*
 * Use this index if you use case insensitive queries
 */
-- create index radreply_UserName_lower on radreply (lower(UserName),Attribute);

/*
 * Table structure for table 'radusergroup'
 */
CREATE TABLE IF NOT EXISTS radusergroup (
	id			serial PRIMARY KEY,
	UserName		text NOT NULL DEFAULT '',
	GroupName		text NOT NULL DEFAULT '',
	priority		integer NOT NULL DEFAULT 0
);
create index radusergroup_UserName on radusergroup (UserName);
/*
 * Use this index if you use case insensitive queries
 */
-- create index radusergroup_UserName_lower on radusergroup (lower(UserName));

--
-- Table structure for table 'radpostauth'
--

CREATE TABLE IF NOT EXISTS radpostauth (
	id			bigserial PRIMARY KEY,
	username		text NOT NULL,
	pass			text,
	reply			text,
	CalledStationId		text,
	CallingStationId	text,
	authdate		timestamp with time zone NOT NULL default now(),
	Class			text
);
CREATE INDEX radpostauth_username_idx ON radpostauth (username);
CREATE INDEX radpostauth_class_idx ON radpostauth (Class);

/*
 * Table structure for table 'nas'
 */
CREATE TABLE IF NOT EXISTS nas (
	id			serial PRIMARY KEY,
	nasname			text NOT NULL,
	shortname		text NOT NULL,
	type			text NOT NULL DEFAULT 'other',
	ports			integer,
	secret			text NOT NULL,
	server			text,
	community		text,
	description		text
);
create index nas_nasname on nas (nasname);

/*
 * Table structure for table 'nasreload'
 */
CREATE TABLE IF NOT EXISTS nasreload (
	NASIPAddress		inet PRIMARY KEY,
	ReloadTime		timestamp with time zone NOT NULL
);


CREATE USER ${POSTGRES_REPLICATION_USER} WITH PASSWORD '${POSTGRES_REPLICATION_PASSWORD}';

GRANT ALL PRIVILEGES ON TABLE eduroam_eduroamaccount TO ${POSTGRES_REPLICATION_USER};
GRANT USAGE ON SCHEMA public TO ${POSTGRES_REPLICATION_USER};

CREATE SUBSCRIPTION eduroam_sub 
CONNECTION 'host=postgres port=5432 dbname=django user=${POSTGRES_REPLICATION_USER} password=${POSTGRES_REPLICATION_PASSWORD}'
PUBLICATION eduroam_pub;

/*
 * setup.sql -- PostgreSQL commands for creating the RADIUS user.
 *
 *	WARNING: You should change 'localhost' and 'radpass'
 *		 to something else.  Also update raddb/mods-available/sql
 *		 with the new RADIUS password.
 *
 */

/*
 *  Create default administrator for RADIUS
 *
 */
CREATE USER radius WITH PASSWORD '${POSTGRES_RADIUS_PASSWORD}';

GRANT SELECT ON vlan_override TO radius;

/*
 *  The server can read the authorisation data
 *
 */
GRANT SELECT ON radcheck TO radius;
GRANT SELECT ON radreply TO radius;
GRANT SELECT ON radusergroup TO radius;
GRANT SELECT ON radgroupcheck TO radius;
GRANT SELECT ON radgroupreply TO radius;

/*
 *  The server can write accounting and post-auth data
 *
 */
GRANT SELECT, INSERT, UPDATE on radacct TO radius;
GRANT SELECT, INSERT, UPDATE on radpostauth TO radius;

/*
 *  The server can read the NAS data
 *
 */
GRANT SELECT ON nas TO radius;

/*
 *  In the case of the "lightweight accounting-on/off" strategy, the server also
 *  records NAS reload times
 *
 */
GRANT SELECT, INSERT, UPDATE ON nasreload TO radius;

/*
 * Grant permissions on sequences
 *
 */
GRANT USAGE, SELECT ON SEQUENCE radreply_id_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE radusergroup_id_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE radgroupcheck_id_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE radgroupreply_id_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE radacct_radacctid_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE radpostauth_id_seq TO radius;
GRANT USAGE, SELECT ON SEQUENCE nas_id_seq TO radius;


EOSQL

