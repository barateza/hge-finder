# API Systems V1 / API / EDSM - Elite Dangerous Star Map

### API Systems v1

Last Revision: _Oct 6, 2020, 1:58:35 PM_

All messages returned by the API are in JSON. Most queries work with **GET** but they should also be compatible with **POST** requests.

Get information about a system

**HTTP Request:** `GET https://www.edsm.net/api-v1/system`

Parameter

Default

Description

**systemName**\*

`NULL`

The system name

 

 

showId

`0`

Set to `1` to get our internal ID for this system.

showCoordinates

`0`

Set to `1` to get the system coordinates.  
If coordinates are unknown, the _coords_ key will not be returned.

showPermit

`0`

Set to `1` to get the system permit if there is one.  
If the permit is named, also return `permitName`.

showInformation

`0`

Set to `1` to get the system information like allegiance, government...  
If no information are stored, an empty array will be returned.

showPrimaryStar

`0`

Set to `1` to get the system primary star if known.  
If no primary star is stored, a `NULL` will be returned.

 

includeHidden

`0`

Set to `1` to get system even if hidden in the database.  
Hidden system are generally typo errors, renamed system in the game...

**Output:**

{
    name            : "Merope",
    coords          : {
        x               : -78.59375,
        y               : -149.625,
        z               : -340.53125
    },
    information     : {
        allegiance      : "Federation",
        government      : "Democracy",
        faction         : "Pleiades Resource Enterprise",
        factionState    : "Expansion",
        population      : 850000,
        security        : "Medium",
        economy         : "Industrial"
    },
    primaryStar     : {
        type            : "B (Blue-White) Star",
        name            : "Merope",
        isScoopable     : true
    }
}

Parameter

Description

**name**

Name of the system.

**id**

Internal ID of the system.

**coords**

Array of coordinates if known.

**duplicates**

When requesting `showId`, return the systems ID having the exact same name in the game.

 

**requirePermit**

`true`/`false`.

**permitName**

Name of required permit, if not Unknown.

**information**

Array of information if known.

*   **allegiance** : The current allegiance of the system.
*   **government** : The current government of the system.
*   **faction** : The current faction of the system.
*   **population** : The current population of the system.

**primaryStar**

Array of information concerning the primary star of the system if known.

*   **type** : The type of the primary star. See our [Celestial bodies FAQ](/en/faq/bodies) for a list of all types.
*   **name** : The name of the primary star.
*   **isScoopable** : `TRUE`/`FALSE` depending if the primary star type is scoopable for fuel.

 

**hidden\_at**

When requesting `includeHidden`, return the `datetime` when the system was hidden.

**mergedTo**

When requesting `includeHidden` and `showId`, return the system ID where the system was renamed.  
Eg: **Eol Prou RS-T d3-94 \[#5553159\]** was renamed to **Colonia (Jaques Station) \[#3384966\]**.

Get information about systems

**HTTP Request:** `GET https://www.edsm.net/api-v1/systems`

Parameter

Default

Description

**systemName**

`NULL`

The systems name to retrieve, can be a start of a name or an array of specific names.  
Eg: `systemName=Eol Prou` or `systemName[]=Achali&systemName[]=Sol`

 

**showId** / **showCoordinates** / **showPermit** / **showInformation** / **showPrimaryStar**

 

See [**Get information about a system**](#endPointSystem) endpoint.

 

startDateTime  
YYYY-MM-DD HH:MM:SS

`NULL`

If you only want to receive systems updated after a specific date & time, use this parameter.

That parameter is inclusive. All dates must be UTC.

startDateTime and endDateTime can be use together or separately, but the maximum interval will be `3 DAY`.  
If both are set, endDateTime will be used to calculate the interval.

endDateTime  
YYYY-MM-DD HH:MM:SS

`NULL`

If you only want to receive systems updated before a specific date & time, use this parameter.

That parameter is inclusive. All dates must be UTC.

startDateTime and endDateTime can be use together or separately, but the maximum interval will be `3 DAY`.  
If both are set, endDateTime will be used to calculate the interval.

 

**onlyKnownCoordinates**

`NULL`

Set to `1` to get only systems with known coordinates.

**onlyUnknownCoordinates**

`NULL`

Set to `1` to get only systems without coordinates.

**includeHidden**

 

See [**Get information about a system**](#endPointSystem) endpoint.

**Output:**

\[
    {
        name        : "Eol Prou RS-T d3-94",
        id          : 5553159,
        mergedTo    : 3384966,
        hidden\_at   : "2016-09-27 07:21:51"
    },
    {
        name        : "Sol",
        id          : 27,
        coords      : {
            x           : 0,
            y           : 0,
            z           : 0
        }
    },
    {
        name        : "2MASS J00014645-2946387",
        id          : 9664483,
        duplicates  : \[
            1946723
        \],
        coords      : {
            x           : -46.5625,
            y           : -831.78125,
            z           : 158.375
        }
    }
\]

Parameter

Description

**name**

Name of the system.

 

**id** / **duplicates** / **coords** / **requirePermit** / **permitName** / **information** / **primaryStar**

See [**Get information about a system**](#endPointSystem) endpoint.

 

**hidden\_at** / **mergedTo**

See [**Get information about a system**](#endPointSystem) endpoint.

Get systems in a sphere radius

**HTTP Request:** `GET https://www.edsm.net/api-v1/sphere-systems`

Parameter

Default

Description

**systemName**\*

`NULL`

The system name which will be the center of the sphere.

**x**\* / **y**\* / **z**\*

`NULL`

If you don't want to use a system name, you can use coordinates as the center of the sphere.

minRadius

`0`

Set to a value between 0 and `radius` to reduce the returned results.  
In _ly_.

radius

`50`

Set to the desired radius  
In _ly_. Maximum value is _100_.

 

**showId** / **showCoordinates** / **showPermit** / **showInformation** / **showPrimaryStar**

 

See [**Get information about a system**](#endPointSystem) endpoint.

**Output:**

\[
    {
        distance    : 99.89,
        name        : "Pleiades Sector II-S b4-2",
        id          : 2069591,
        coords      : {
            x           : -177.03125,
            y           : -136.53125,
            z           : -329.75
        }
    },
    {
        distance    : 97.86,
        name        : "Pleiades Sector EC-U b3-3",
        id          : 3421818,
        coords      : {
            x           : -174.40625,
            y           : -141.40625,
            z           : -358.6875
        }
    }
\]

Parameter

Description

**distance**

Distance in _ly_ from the center of the sphere.

**name**

Name of the system.

 

**id** / **coords** / **requirePermit** / **permitName** / **information** / **primaryStar**

See [**Get information about a system**](#endPointSystem) endpoint.

Get systems in a cube

**HTTP Request:** `GET https://www.edsm.net/api-v1/cube-systems`

Parameter

Default

Description

**systemName**\*

`NULL`

The system name which will be the center of the sphere.

**x**\* / **y**\* / **z**\*

`NULL`

If you don't want to use a system name, you can use coordinates as the center of the sphere.

size

`100`

Set to the desired size of the cube  
In _ly_. Maximum value is _200_.

 

**showId** / **showCoordinates** / **showPermit** / **showInformation** / **showPrimaryStar**

 

See [**Get information about a system**](#endPointSystem) endpoint.

**Output:**

\[
    {
        name        : "Pleiades Sector II-S b4-2",
        id          : 2069591,
        coords      : {
            x           : -177.03125,
            y           : -136.53125,
            z           : -329.75
        }
    },
    {
        name        : "Pleiades Sector EC-U b3-3",
        id          : 3421818,
        coords      : {
            x           : -174.40625,
            y           : -141.40625,
            z           : -358.6875
        }
    }
\]

Parameter

Description

**name**

Name of the system.

 

**id** / **coords** / **requirePermit** / **permitName** / **information** / **primaryStar**

See [**Get information about a system**](#endPointSystem) endpoint.