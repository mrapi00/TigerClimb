from search import create_session
from database_defs import Base, Routes, RouteEdits

def main():
    engine, session = create_session()
    Base.metadata.create_all(engine)

    with open('routes_import.csv') as routes_file:
        routes_file.readline() # discard header

        route_line = routes_file.readline()
        while route_line != '':
            route_line = route_line.rstrip('\n')
            arr = route_line.split(',')

            route_id = int(arr[0])
            name = arr[1]
            grade = float(arr[2])
            consensus_grade = float(arr[3])
            tape_col = arr[4]
            tape_col2 = arr[5]
            if arr[6] == '':
                date_created = "01/01/1980"
            else:
                date_created = arr[6]
            descrip = arr[7]
            status = arr[8]
            rope = int(arr[9])
            route_type = arr[10]

            session.add(RouteEdits(version=0, netid='dw26'))
            new_route = Routes(name=name, grade=grade,
            consensus_grade=consensus_grade, tape_col=tape_col,
            tape_col2=tape_col2, date_created=date_created, descrip=descrip,
            status=status, rope=rope, route_type=route_type)

            session.add(new_route)
            route_line = routes_file.readline()

        session.commit()

    session.close()
    engine.dispose()

if __name__ == '__main__':
    main()