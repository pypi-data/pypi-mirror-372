#  Copyright (C) GridGain Systems. All Rights Reserved.
#  _________        _____ __________________        _____
#  __  ____/___________(_)______  /__  ____/______ ____(_)_______
#  _  / __  __  ___/__  / _  __  / _  / __  _  __ `/__  / __  __ \
#  / /_/ /  _  /    _  /  / /_/ /  / /_/ /  / /_/ / _  /  _  / / /
#  \____/   /_/     /_/   \_,__/   \____/   \__,_/  /_/   /_/ /_/

project(ignite-client-compatibility-test)

set(TARGET ${PROJECT_NAME})

set(SOURCES
    main.cpp
    continuous_query_test_ign_version.cpp
    ignite_xml_unit_test_result_printer.cpp
)

ignite_test(${TARGET} SOURCES ${SOURCES} LIBS ignite-test-common ignite3-client)
